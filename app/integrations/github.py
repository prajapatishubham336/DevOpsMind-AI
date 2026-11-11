from __future__ import annotations

import base64
import os
from typing import Any
from urllib.parse import quote

import httpx

try:
    from app.config import GITHUB_TOKEN
except Exception:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API = "https://api.github.com"
REQUEST_TIMEOUT = 20.0


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "DevOpsMind-AI",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


async def github_request(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """Make a safe GitHub REST API GET request."""
    url = f"{GITHUB_API}/{endpoint.lstrip('/')}"

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url, headers=_headers(), params=params)

    if response.status_code == 404:
        raise RuntimeError("GitHub resource not found. Check owner, repository, branch, and path.")

    if response.status_code == 401:
        raise RuntimeError("GitHub authentication failed. Check GITHUB_TOKEN.")

    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            raise RuntimeError("GitHub API rate limit reached. Add or check GITHUB_TOKEN.")
        raise RuntimeError(f"GitHub access forbidden: {response.text[:500]}")

    response.raise_for_status()
    return response.json()


async def get_repository(owner: str, repo: str) -> dict[str, Any]:
    owner = quote(owner.strip(), safe="")
    repo = quote(repo.strip(), safe="")
    return await github_request(f"repos/{owner}/{repo}")


async def get_repository_tree(
    owner: str,
    repo: str,
    branch: str | None = None,
) -> dict[str, Any]:
    """Return recursive tree information, including GitHub's truncation flag."""
    if not branch:
        metadata = await get_repository(owner, repo)
        branch = metadata.get("default_branch") or "main"

    owner_q = quote(owner.strip(), safe="")
    repo_q = quote(repo.strip(), safe="")
    branch_q = quote(branch, safe="")

    tree_data = await github_request(
        f"repos/{owner_q}/{repo_q}/git/trees/{branch_q}",
        params={"recursive": "1"},
    )

    files = []
    for item in tree_data.get("tree", []):
        if item.get("type") != "blob":
            continue
        files.append(
            {
                "path": item.get("path", ""),
                "type": item.get("type", "blob"),
                "size": item.get("size", 0),
                "sha": item.get("sha"),
            }
        )

    return {
        "files": files,
        "total_files": len(files),
        "truncated": bool(tree_data.get("truncated", False)),
        "branch": branch,
    }


async def get_repository_files(
    owner: str,
    repo: str,
    branch: str | None = None,
) -> list[dict[str, Any]]:
    """
    Backwards-compatible helper: returns a list of file metadata records,
    suitable for the existing GET /github/files/{owner}/{repo} endpoint.
    """
    tree = await get_repository_tree(owner, repo, branch)
    return tree["files"]


async def get_file_content(
    owner: str,
    repo: str,
    path: str,
    ref: str | None = None,
    max_bytes: int = 1_000_000,
) -> str:
    """Fetch and decode a text file through GitHub's Contents API."""
    owner_q = quote(owner.strip(), safe="")
    repo_q = quote(repo.strip(), safe="")
    path_q = quote(path, safe="/")

    params = {"ref": ref} if ref else None
    data = await github_request(
        f"repos/{owner_q}/{repo_q}/contents/{path_q}",
        params=params,
    )

    if isinstance(data, list):
        raise RuntimeError(f"{path} is a directory, not a file.")

    if data.get("type") != "file":
        raise RuntimeError(f"{path} is not a regular file.")

    size = int(data.get("size") or 0)
    if size > max_bytes:
        raise RuntimeError(f"{path} is too large to inspect ({size} bytes).")

    encoded = data.get("content") or ""
    if data.get("encoding") != "base64" or not encoded.strip():
        raise RuntimeError(f"GitHub did not return base64 text content for {path}.")

    try:
        decoded = base64.b64decode(encoded).decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(f"Could not decode {path}: {exc}") from exc

    return decoded
