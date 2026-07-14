import logging

from backend.core.log_sanitize import redact_text, safe_extra
from backend.core.logging_config import RedactionFilter, JsonLogFormatter
from config.settings import settings


def test_redact_text_never_echoes_body() -> None:
    secret = "Person A: confidential dialogue"
    assert secret not in redact_text(secret)
    assert "len=" in redact_text(secret)


def test_safe_extra_strips_sensitive_keys() -> None:
    cleaned = safe_extra(
        transcript_id="tid",
        raw_text="SECRET BODY",
        prompt="SYSTEM PROMPT",
        turn_count=2,
    )
    assert cleaned["transcript_id"] == "tid"
    assert cleaned["turn_count"] == 2
    assert "SECRET" not in str(cleaned["raw_text"])
    assert "SYSTEM" not in str(cleaned["prompt"])


def test_redaction_filter_scrubs_extra(monkeypatch) -> None:
    monkeypatch.setattr(settings, "log_redact", True)
    record = logging.LogRecord(
        name="test.redact",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="module failed",
        args=(),
        exc_info=None,
    )
    record.raw_output = "DIALOGUE SECRET XYZ"
    record.event = "module.run.failed"
    assert RedactionFilter().filter(record) is True
    assert "DIALOGUE SECRET XYZ" not in str(record.raw_output)
    assert "redacted" in str(record.raw_output).lower()

    payload = JsonLogFormatter().format(record)
    assert "DIALOGUE SECRET XYZ" not in payload
    assert "module failed" in payload
