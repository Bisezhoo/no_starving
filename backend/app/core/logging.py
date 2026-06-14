import json
import logging as python_logging
import re
from typing import Any


SECRET_KEYWORDS = ("authorization", "api_key", "apikey", "secret", "token", "key")


def get_logger(name: str) -> python_logging.Logger:
    return python_logging.getLogger(name)


def log_event(
    logger: python_logging.Logger,
    event: str,
    *,
    settings: Any | None = None,
    fields: dict[str, Any] | None = None,
    level: int = python_logging.INFO,
    exc_info: bool = False,
) -> None:
    payload = {"event": event}
    for key, value in (fields or {}).items():
        payload[key] = sanitize_field(key, value, settings)
    logger.log(
        level,
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        exc_info=exc_info,
    )


def summarize_sensitive_text(value: Any, *, allow_full: bool = False) -> Any:
    if value is None:
        return {"present": False, "length": 0}
    text = str(value)
    if allow_full:
        return text
    return {"present": bool(text), "length": len(text)}


def summarize_tool_arguments(arguments: dict[str, Any], settings: Any | None = None) -> dict[str, Any]:
    summarized: dict[str, Any] = {}
    for key, value in arguments.items():
        if isinstance(value, str) and _has_cjk(value):
            summarized[key] = summarize_sensitive_text(value, allow_full=False)
        else:
            summarized[key] = sanitize_field(key, value, settings)
    return summarized


def mask_secret(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}***{text[-4:]}"


def sanitize_field(key: str, value: Any, settings: Any | None = None) -> Any:
    normalized_key = key.replace("_", "").replace("-", "").lower()
    if normalized_key == "usermessage":
        return summarize_sensitive_text(value, allow_full=_enabled(settings, "log_full_user_message"))
    if normalized_key == "sourcetext":
        return summarize_sensitive_text(value, allow_full=_enabled(settings, "log_full_source_text"))
    if normalized_key == "systemprompt":
        return summarize_sensitive_text(value, allow_full=_enabled(settings, "log_full_system_prompt"))
    if normalized_key == "headers":
        return _sanitize_headers(value, settings)
    if _is_secret_key(normalized_key):
        return _mask_header_or_secret(value)
    if isinstance(value, dict):
        return {nested_key: sanitize_field(nested_key, nested_value, settings) for nested_key, nested_value in value.items()}
    if isinstance(value, list):
        return [sanitize_field(key, item, settings) for item in value]
    return value


def _sanitize_headers(value: Any, settings: Any | None) -> Any:
    if not isinstance(value, dict):
        return summarize_sensitive_text(value, allow_full=_enabled(settings, "log_sensitive_external_headers"))
    if not _enabled(settings, "log_sensitive_external_headers"):
        return {
            header_name: summarize_sensitive_text(header_value, allow_full=False)
            for header_name, header_value in value.items()
        }
    return {
        header_name: _mask_header_or_secret(header_value) if _is_secret_key(header_name.lower()) else header_value
        for header_name, header_value in value.items()
    }


def _mask_header_or_secret(value: Any) -> Any:
    if not isinstance(value, str):
        return mask_secret(value)
    match = re.match(r"^(Bearer\s+)(.+)$", value, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)}{mask_secret(match.group(2))}"
    return mask_secret(value)


def _enabled(settings: Any | None, field: str) -> bool:
    return bool(getattr(settings, field, False))


def _is_secret_key(key: str) -> bool:
    return any(keyword in key for keyword in SECRET_KEYWORDS)


def _has_cjk(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))
