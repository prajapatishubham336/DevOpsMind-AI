from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm


def content_to_text(content: Any) -> str:
    """Normalize LangChain message content into plain text."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts)

    return str(content or "")


async def invoke_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the configured ChatGroq model asynchronously."""
    llm = get_llm()
    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return content_to_text(getattr(response, "content", response)).strip()


def is_token_limit_error(exc: Exception) -> bool:
    """Recognize Groq/LangChain prompt-size and TPM errors."""
    message = str(exc).lower()
    markers = (
        "413",
        "tokens per minute",
        "token per minute",
        "tpm",
        "request too large",
        "reduce your message size",
        "rate_limit_exceeded",
    )
    return any(marker in message for marker in markers)
