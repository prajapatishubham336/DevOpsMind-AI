from __future__ import annotations

from app.agents.common import invoke_llm


SYSTEM_PROMPT = """
You are the Log Analysis Agent of DevOpsMind AI.

Analyze only the supplied logs and user-provided context.
Be precise and concise. Do not invent missing stack traces, file names,
database engines, infrastructure, or runtime facts.

Important evidence rules:
- Port 5432 is commonly used by PostgreSQL, but the port alone does not prove
  that the application uses PostgreSQL.
- "Connection refused" means the TCP connection was actively rejected at the
  target address/port; it does not by itself prove why.
- Separate CONFIRMED evidence, POSSIBLE causes, and UNKNOWN information.
- Do not say a cause is confirmed unless the log directly proves it.
- Give practical investigation steps before recommending disruptive actions.

Return these sections:
1. Error / symptom
2. Severity and impact (explain uncertainty)
3. Confirmed evidence
4. Possible causes (clearly labelled hypotheses)
5. Unknown information
6. Prioritized investigation steps
"""


async def log_analysis_agent(state: dict) -> dict:
    logs = (state.get("logs") or "").strip()
    repo_context = (state.get("repo_context") or "Not provided").strip()

    if not logs:
        return {"log_analysis": "Skipped: No application logs were provided."}

    # Bound input so this agent does not consume the entire model TPM window.
    bounded_logs = logs[:6000]
    bounded_context = repo_context[:1000]

    user_prompt = f"""
USER-PROVIDED LOGS:
{bounded_logs}

USER-PROVIDED REPOSITORY / ENVIRONMENT CONTEXT:
{bounded_context}

Analyze the evidence. Keep the report under approximately 450 words.
"""

    try:
        result = await invoke_llm(SYSTEM_PROMPT, user_prompt)
        return {"log_analysis": result or "Log analysis returned an empty response."}
    except Exception as exc:
        fallback = (
            "Log analysis could not be completed by the LLM.\n"
            f"Error: {exc}\n\n"
            "The supplied logs are retained as evidence, but no AI root-cause "
            "conclusion is being asserted. Check the model/API availability "
            "and retry."
        )
        return {
            "log_analysis": fallback,
            "agent_errors": state.get("agent_errors", []) + [f"Log Analysis Agent: {exc}"],
        }
