from __future__ import annotations

import os
from pathlib import PurePosixPath

from app.agents.common import invoke_llm, is_token_limit_error
from app.integrations.github import (
    get_file_content,
    get_repository,
    get_repository_tree,
)

# Conservative defaults for the Groq 8,000 TPM environment observed in testing.
MAX_FILES = 4
MAX_FILE_CHARS = 2500
MAX_TOTAL_CHARS = 8000

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "site-packages", "dist", "build", ".next", "coverage",
}
SKIP_SUFFIXES = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip",
    ".whl", ".sqlite", ".db", ".pyc", ".lock",
}
SECRET_MARKERS = (
    "id_rsa", "private_key", "credentials", "secrets.json",
    ".env", "token", "password",
)

PRIORITY_NAMES = {
    "requirements.txt": 100,
    "pyproject.toml": 95,
    "dockerfile": 90,
    "docker-compose.yml": 90,
    "compose.yml": 90,
    "main.py": 85,
    "app.py": 80,
    "config.py": 80,
    "settings.py": 80,
    "database.py": 75,
    "readme.md": 60,
}


def _is_safe_text_file(path: str, size: int) -> bool:
    lower = path.lower()
    parts = PurePosixPath(lower).parts

    if any(part in SKIP_DIRS for part in parts):
        return False
    if any(marker in lower for marker in SECRET_MARKERS):
        if not lower.endswith((".env.example", ".env.sample")):
            return False
    if any(lower.endswith(suffix) for suffix in SKIP_SUFFIXES):
        return False
    if size > 1_000_000:
        return False

    allowed = (
        lower.endswith((".py", ".toml", ".ini", ".cfg", ".yaml", ".yml",
                        ".json", ".md", ".txt", ".sh", ".conf"))
        or PurePosixPath(lower).name in {"dockerfile", "makefile"}
    )
    return allowed


def select_relevant_files(files: list[dict], logs: str = "") -> list[dict]:
    """Rank source/config files and select a small, relevant subset."""
    log_terms = {
        term.lower()
        for term in ("database", "connection", "postgres", "sql", "timeout",
                     "import", "module", "api", "500", "error", "config")
        if term.lower() in (logs or "").lower()
    }

    candidates = []
    for item in files:
        path = item.get("path", "")
        size = int(item.get("size") or 0)
        if not path or not _is_safe_text_file(path, size):
            continue

        name = PurePosixPath(path).name.lower()
        score = PRIORITY_NAMES.get(name, 0)

        if path.lower().endswith(".py"):
            score += 30
        if any(term in path.lower() for term in log_terms):
            score += 25
        if any(term in path.lower() for term in
               ("database", "db", "postgres", "sql", "config", "settings",
                "connection", "main", "app", "test")):
            score += 15

        candidates.append((score, item))

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in candidates[:MAX_FILES]]


def format_source_code(path: str, source: str, remaining_chars: int) -> str:
    allowed = min(MAX_FILE_CHARS, max(0, remaining_chars))
    if allowed <= 0:
        return ""

    clipped = source[:allowed]
    numbered = "\n".join(
        f"{index:04d}: {line}"
        for index, line in enumerate(clipped.splitlines(), start=1)
    )
    if len(source) > allowed:
        numbered += "\n[FILE CONTENT TRUNCATED]"
    return f"\n--- FILE: {path} ---\n{numbered}\n"


def _source_context(inspected: list[dict], limit: int) -> str:
    chunks: list[str] = []
    remaining = limit

    for item in inspected:
        if remaining <= 0:
            break
        block = format_source_code(item["path"], item["content"], remaining)
        if block:
            chunks.append(block)
            remaining -= len(block)

    return "\n".join(chunks)


SYSTEM_PROMPT = """
You are the GitHub Code Intelligence and Code Review Agent of DevOpsMind AI.

You receive verified GitHub metadata, a file tree, selected retrieved source files,
and user-provided runtime logs.

Rules:
- Only claim that a file was inspected when its content is present in SOURCE CODE.
- Treat repository metadata, retrieved file contents, and user-provided logs as
  different evidence sources.
- Never invent functions, dependencies, configuration values, line numbers,
  commits, pull requests, or code changes.
- Line numbers are approximate line numbers added to the retrieved snippets.
- A file marked truncated was only partially inspected.
- Do not claim PostgreSQL is used unless retrieved source/config/dependencies or
  explicit user context confirms it. Port 5432 alone is not proof.
- If the repository has no matching database code, say that no code-level
  correlation was established.
- Do not claim cloning, Git blame, PR review, or deployment; those operations
  are not implemented here.

Return a concise report with:
1. Confirmed repository facts
2. Files actually inspected
3. Relevant implementation/dependency evidence
4. Correlation with supplied logs
5. Possible issue(s), clearly marked as hypotheses
6. Missing evidence / next inspection steps
"""


async def github_agent(state: dict) -> dict:
    owner = (state.get("github_owner") or "").strip()
    repo = (state.get("github_repo") or "").strip()
    logs = (state.get("logs") or "")[:4000]
    repo_context = (state.get("repo_context") or "Not provided")[:800]

    if not owner or not repo:
        return {
            "github_analysis": "Skipped: GitHub owner and repository were not both provided.",
            "github_data": {},
        }

    try:
        metadata = await get_repository(owner, repo)
        branch = metadata.get("default_branch") or "main"
        tree = await get_repository_tree(owner, repo, branch)
        selected = select_relevant_files(tree["files"], logs)

        inspected: list[dict] = []
        retrieval_errors: list[str] = []

        for item in selected:
            path = item["path"]
            try:
                content = await get_file_content(
                    owner, repo, path, ref=branch, max_bytes=1_000_000
                )
                inspected.append(
                    {
                        "path": path,
                        "sha": item.get("sha"),
                        "size": item.get("size", 0),
                        "content": content,
                        "truncated": len(content) > MAX_FILE_CHARS,
                    }
                )
            except Exception as exc:
                retrieval_errors.append(f"{path}: {exc}")

        # Retry with progressively smaller source context if Groq reports a
        # prompt/TPM-size error. The workflow continues even if all retries fail.
        analysis = ""
        last_error: Exception | None = None

        for source_limit in (MAX_TOTAL_CHARS, 4000, 1800):
            source = _source_context(inspected, source_limit)
            prompt = f"""
REPOSITORY METADATA:
Name: {metadata.get("full_name")}
Description: {metadata.get("description")}
Default branch: {branch}
Primary language field: {metadata.get("language")}
Repository URL: {metadata.get("html_url")}

USER-PROVIDED CONTEXT:
{repo_context}

APPLICATION LOGS:
{logs or "Not provided"}

FILE TREE SUMMARY:
Total files: {tree.get("total_files")}
Tree truncated by GitHub: {tree.get("truncated")}
Selected files: {", ".join(item["path"] for item in selected) or "None"}

RETRIEVED SOURCE CODE:
{source or "No source file content could be retrieved."}

Analyze only the evidence above. Keep the response under approximately 550 words.
"""
            try:
                analysis = await invoke_llm(SYSTEM_PROMPT, prompt)
                break
            except Exception as exc:
                last_error = exc
                if is_token_limit_error(exc):
                    continue
                raise

        if not analysis:
            raise RuntimeError(
                f"GitHub source retrieval succeeded, but AI analysis failed: {last_error}"
            )

        public_inspected = [
            {
                "path": item["path"],
                "sha": item.get("sha"),
                "size": item.get("size", 0),
                "truncated": item["truncated"],
            }
            for item in inspected
        ]

        github_data = {
            "name": metadata.get("name"),
            "full_name": metadata.get("full_name"),
            "description": metadata.get("description"),
            "private": metadata.get("private"),
            "default_branch": branch,
            "html_url": metadata.get("html_url"),
            "language": metadata.get("language"),
            "stars": metadata.get("stargazers_count"),
            "total_files": tree.get("total_files", 0),
            "tree_truncated": tree.get("truncated", False),
            "files": tree.get("files", []),
            "inspected_files": public_inspected,
            "retrieval_errors": retrieval_errors,
        }

        return {
            "github_analysis": analysis,
            "github_data": github_data,
        }

    except Exception as exc:
        return {
            "github_analysis": (
                "GitHub Agent could not complete repository analysis.\n"
                f"Error: {exc}\n"
                "Any metadata or source retrieval completed before the error "
                "should not be interpreted as a successful AI code analysis."
            ),
            "github_data": {
                "retrieval_errors": [str(exc)],
                "inspected_files": [],
            },
            "agent_errors": state.get("agent_errors", []) + [f"GitHub Agent: {exc}"],
        }
