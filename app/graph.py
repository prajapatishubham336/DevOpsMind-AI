from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.common import invoke_llm
from app.agents.manager_agent import manager_agent
from app.agents.log_agent import log_analysis_agent
from app.agents.github_agent import github_agent
from app.agents.monitoring_agent import monitoring_agent
from app.agents.fix_agent import fix_agent


# ---------------------------------------------------------------------------
# STEP 1 COMPATIBILITY: preserve the existing /analyze workflow interface.
# ---------------------------------------------------------------------------

class DevOpsState(TypedDict, total=False):
    logs: str
    repo_context: str
    analysis: str
    fix_suggestion: str


async def _basic_log_node(state: DevOpsState) -> dict:
    prompt = f"""
Analyze these application logs. Separate confirmed evidence from hypotheses.
Do not invent a database engine, file path, or root cause.

LOGS:
{(state.get("logs") or "")[:6000]}

REPOSITORY CONTEXT:
{(state.get("repo_context") or "Not provided")[:1000]}

Return a concise log analysis with error type, impact, confirmed evidence,
possible causes, unknowns, and investigation steps.
"""
    result = await invoke_llm(
        "You are a careful application log analysis assistant.",
        prompt,
    )
    return {"analysis": result}


async def _basic_fix_node(state: DevOpsState) -> dict:
    prompt = f"""
Based on the following analysis, provide a cautious fix recommendation.
Do not claim code was changed or deployed. Separate verified facts from
hypotheses and include verification steps.

LOG ANALYSIS:
{(state.get("analysis") or "")[:3500]}

REPOSITORY CONTEXT:
{(state.get("repo_context") or "Not provided")[:700]}
"""
    result = await invoke_llm(
        "You are a senior debugging assistant. Never invent repository evidence.",
        prompt,
    )
    return {"fix_suggestion": result}


def create_devops_graph():
    workflow = StateGraph(DevOpsState)
    workflow.add_node("log_analysis", _basic_log_node)
    workflow.add_node("fix_suggestion", _basic_fix_node)
    workflow.add_edge(START, "log_analysis")
    workflow.add_edge("log_analysis", "fix_suggestion")
    workflow.add_edge("fix_suggestion", END)
    return workflow.compile()


devops_graph = create_devops_graph()


async def run_analysis(logs: str, repo_context: str = "Not provided") -> dict:
    """Backward-compatible function used by the existing POST /analyze route."""
    result = await devops_graph.ainvoke(
        {
            "logs": logs or "",
            "repo_context": repo_context or "Not provided",
        }
    )
    return {
        "analysis": result.get("analysis", ""),
        "fix_suggestion": result.get("fix_suggestion", ""),
    }


# ---------------------------------------------------------------------------
# STEP 3 & STEP 4: ADVANCED MULTI-AGENT WORKFLOW + SAFETY GATE
# ---------------------------------------------------------------------------

class MultiAgentState(TypedDict, total=False):
    task: str
    logs: str
    repo_context: str
    github_owner: str | None
    github_repo: str | None
    app_id: int | str | None

    manager_plan: str
    active_agents: list[str]
    execution_order: list[str]

    log_analysis: str
    github_analysis: str
    github_data: dict[str, Any]
    monitoring_analysis: str
    fix_suggestion: str
    approval_status: str
    deployment_blocked: bool
    agent_errors: list[str]


ROUTE_MAP = {
    "log_agent": "log_agent",
    "github_agent": "github_agent",
    "monitoring_agent": "monitoring_agent",
    "fix_agent": "fix_agent",
}


def _next_node(state: MultiAgentState, current_node: str) -> str:
    order = state.get("execution_order", [])

    if current_node == "manager":
        next_index = 0
    else:
        try:
            next_index = order.index(current_node) + 1
        except ValueError:
            next_index = len(order)

    if next_index < len(order):
        return order[next_index]
    return "fix_agent"


def create_multi_agent_graph():
    workflow = StateGraph(MultiAgentState)

    workflow.add_node("manager", manager_agent)
    workflow.add_node("log_agent", log_analysis_agent)
    workflow.add_node("github_agent", github_agent)
    workflow.add_node("monitoring_agent", monitoring_agent)
    workflow.add_node("fix_agent", fix_agent)

    workflow.add_edge(START, "manager")

    def make_router(source_node: str):
        def router(state: MultiAgentState) -> str:
            return _next_node(state, source_node)
        return router

    for source in ("manager", "log_agent", "github_agent", "monitoring_agent"):
        workflow.add_conditional_edges(
            source,
            make_router(source),
            ROUTE_MAP,
        )

    workflow.add_edge("fix_agent", END)
    return workflow.compile()


multi_agent_graph = create_multi_agent_graph()


def _request_value(request: Any, key: str, default: Any = None) -> Any:
    if isinstance(request, dict):
        return request.get(key, default)
    return getattr(request, key, default)


async def run_multi_agent(request: Any) -> dict:
    """Run manager -> selected specialists -> fix synthesis -> safety check."""
    initial_state: MultiAgentState = {
        "task": _request_value(request, "task", "") or "",
        "logs": _request_value(request, "logs", "") or "",
        "repo_context": _request_value(request, "repo_context", "Not provided") or "Not provided",
        "github_owner": _request_value(request, "github_owner"),
        "github_repo": _request_value(request, "github_repo"),
        "app_id": _request_value(request, "app_id"),
        "manager_plan": "",
        "active_agents": [],
        "execution_order": [],
        "log_analysis": "",
        "github_analysis": "",
        "github_data": {},
        "monitoring_analysis": "",
        "fix_suggestion": "",
        "approval_status": "pending_human_approval",
        "deployment_blocked": True,
        "agent_errors": [],
    }

    result = await multi_agent_graph.ainvoke(initial_state)
    errors = result.get("agent_errors", [])

    return {
        "status": "partial_success" if errors else "success",
        "manager_plan": result.get("manager_plan", ""),
        "active_agents": result.get("active_agents", []),
        "log_analysis": result.get("log_analysis", ""),
        "github_analysis": result.get("github_analysis", ""),
        "github_data": result.get("github_data", {}),
        "monitoring_analysis": result.get(
            "monitoring_analysis", "Skipped: No application ID provided."
        ),
        "fix_suggestion": result.get("fix_suggestion", ""),
        "approval_status": result.get("approval_status", "pending_human_approval"),
        "deployment_blocked": result.get("deployment_blocked", True),
        "agent_errors": errors,
    }