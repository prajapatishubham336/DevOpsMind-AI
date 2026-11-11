from __future__ import annotations

from typing import Any


def manager_agent(state: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministic manager/router.

    Routing is intentionally rule-based so that an extra LLM call does not
    consume the Groq TPM budget before the specialist agents run.
    """
    task = (state.get("task") or "").strip()
    logs = (state.get("logs") or "").strip()
    owner = (state.get("github_owner") or "").strip()
    repo = (state.get("github_repo") or "").strip()
    app_id = state.get("app_id")

    execution_order: list[str] = []
    active_agents: list[str] = []

    if logs:
        execution_order.append("log_agent")
        active_agents.append("Log Analysis Agent")

    if owner and repo:
        execution_order.append("github_agent")
        active_agents.append("GitHub Code Intelligence Agent")

    if app_id is not None:
        execution_order.append("monitoring_agent")
        active_agents.append("Monitoring Agent")

    if not execution_order:
        active_agents.append("No specialist agent selected")

    plan_lines = [
        "DEVOPSMIND AI - MANAGER EXECUTION PLAN",
        "",
        f"USER TASK: {task or 'No task description provided.'}",
        "",
        "SELECTED AGENTS:",
        ", ".join(active_agents),
        "",
        "EXECUTION PLAN:",
    ]

    if "log_agent" in execution_order:
        plan_lines.append(
            "1. Log Analysis Agent: classify the supplied log evidence, "
            "severity, symptoms, and possible causes without treating "
            "unverified hypotheses as facts."
        )

    if "github_agent" in execution_order:
        plan_lines.append(
            "2. GitHub Code Intelligence Agent: retrieve repository metadata, "
            "file paths, and a small set of relevant source/configuration files; "
            "correlate retrieved code with the supplied logs."
        )

    if "monitoring_agent" in execution_order:
        plan_lines.append(
            "3. Monitoring Agent: load the registered application and perform "
            "a live health check using the existing monitoring integration."
        )

    plan_lines.extend(
        [
            "",
            "FINAL SYNTHESIS:",
            "The Fix Agent will combine only the evidence returned by the "
            "selected agents, separate confirmed facts from hypotheses, and "
            "provide actionable remediation and verification steps.",
            "",
            "EXECUTION RULES:",
            "- Do not invent source files, line numbers, commits, pull requests, or runtime state.",
            "- Do not claim PostgreSQL solely because port 5432 appears in a log.",
            "- Do not claim that code was modified or deployed.",
            "- State clearly when an agent or data source was unavailable.",
            "- GitHub source retrieval and LLM analysis are separate operations.",
        ]
    )

    return {
        "manager_plan": "\n".join(plan_lines),
        "active_agents": active_agents,
        "execution_order": execution_order,
        "agent_errors": state.get("agent_errors", []),
    }
