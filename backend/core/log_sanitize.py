"""Sanitize log extras and text so sensitive content stays out of CloudWatch."""

from __future__ import annotations

from typing import Any

_DENY_KEYS = frozenset(
    {
        "raw_text",
        "raw_output",
        "parsed_output",
        "prompt",
        "prompts",
        "messages",
        "content",
        "transcript",
        "quote_text",
        "report_json",
        "database_url",
        "hf_token",
        "api_key",
        "password",
        "secret",
        "authorization",
    }
)


def redact_text(value: Any, *, max_len: int = 0) -> str:
    """Replace sensitive text with a length marker (never emit the original)."""
    if value is None:
        return "[redacted len=0]"
    text = str(value)
    if max_len > 0 and len(text) <= max_len:
        return text
    return f"[redacted len={len(text)}]"


def safe_extra(**kwargs: Any) -> dict[str, Any]:
    """Drop or redact forbidden keys before attaching to logging ``extra``."""
    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        lowered = key.lower()
        if lowered in _DENY_KEYS or any(part in lowered for part in ("secret", "password", "token")):
            if value is None:
                continue
            out[key] = redact_text(value)
            continue
        out[key] = value
    return out
