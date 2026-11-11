from __future__ import annotations

from typing import Any

from app.monitoring.health import check_website
from app.storage.database import get_app, save_health_check


def _record_value(record: Any, key: str, fallback_index: int | None = None) -> Any:
    if record is None:
        return None
    if isinstance(record, dict):
        return record.get(key)
    try:
        return record[key]
    except Exception:
        pass
    if fallback_index is not None:
        try:
            return record[fallback_index]
        except Exception:
            pass
    return getattr(record, key, None)


def _save_check_compat(app_id: int, result: dict) -> str | None:
    """Try common signatures used by the existing Step 2 storage helper."""
    try:
        save_health_check(
            app_id=app_id,
            status=result.get("status"),
            status_code=result.get("status_code"),
            response_time_ms=result.get("response_time_ms"),
            message=result.get("message"),
        )
        return None
    except TypeError:
        pass
    except Exception as exc:
        return str(exc)

    try:
        save_health_check(
            app_id,
            result.get("status"),
            result.get("status_code"),
            result.get("response_time_ms"),
            result.get("message"),
        )
        return None
    except TypeError:
        pass
    except Exception as exc:
        return str(exc)

    try:
        save_health_check(app_id, result)
        return None
    except Exception as exc:
        return str(exc)


async def monitoring_agent(state: dict) -> dict:
    raw_app_id = state.get("app_id")
    if raw_app_id is None:
        return {"monitoring_analysis": "Skipped: No application ID provided."}

    try:
        app_id = int(raw_app_id)
        app_record = get_app(app_id)
        if not app_record:
            return {
                "monitoring_analysis": (
                    f"No monitored application was found for app_id={app_id}."
                )
            }

        # Step 2 database rows are expected to expose name and url fields.
        app_name = _record_value(app_record, "name", 1) or f"Application {app_id}"
        url = _record_value(app_record, "url", 2)

        if not url:
            return {
                "monitoring_analysis": (
                    f"Application {app_name} (id={app_id}) has no URL in storage."
                )
            }

        result = await check_website(url)
        save_warning = _save_check_compat(app_id, result)

        lines = [
            f"Application: {app_name}",
            f"URL: {url}",
            f"Status: {result.get('status', 'unknown')}",
            f"HTTP status code: {result.get('status_code')}",
            f"Response time (ms): {result.get('response_time_ms')}",
            f"Message: {result.get('message', 'No message returned.')}",
        ]
        if save_warning:
            lines.append(f"Warning: health check result could not be saved: {save_warning}")

        return {"monitoring_analysis": "\n".join(lines)}

    except Exception as exc:
        return {
            "monitoring_analysis": f"Monitoring Agent failed: {exc}",
            "agent_errors": state.get("agent_errors", []) + [f"Monitoring Agent: {exc}"],
        }
