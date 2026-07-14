import json
import logging
from datetime import UTC, datetime

from backend.core.log_context import (
    module_id_var,
    module_run_id_var,
    request_id_var,
    workflow_run_id_var,
)
from backend.core.log_sanitize import _DENY_KEYS, redact_text
from config.settings import settings

_STANDARD_EXTRA_KEYS = (
    "event",
    "request_id",
    "workflow_run_id",
    "module_run_id",
    "module_id",
    "error_type",
    "run_id",
    "workflow_id",
    "duration_ms",
    "status",
    "model_id",
    "retry_count",
    "transcript_id",
    "source_type",
    "export_format",
    "purged_count",
    "retention_days",
    "turn_count",
    "quote_count",
)


class RedactionFilter(logging.Filter):
    """Strip denied ``extra`` keys and rewrite huge free-text messages when enabled."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not settings.log_redaction_enabled:
            return True
        for key in list(record.__dict__.keys()):
            if key.lower() in _DENY_KEYS:
                value = getattr(record, key, None)
                setattr(record, key, redact_text(value))
        msg = record.getMessage()
        # Belt-and-suspenders: overly long messages often contain pasted dialogue/prompts.
        if isinstance(record.msg, str) and len(record.msg) > 500:
            record.msg = redact_text(record.msg)
            record.args = ()
        elif len(msg) > 2000:
            record.msg = redact_text(msg)
            record.args = ()
        return True


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in _STANDARD_EXTRA_KEYS:
            value = getattr(record, key, None)
            if value is None and key == "request_id":
                value = request_id_var.get()
            elif value is None and key == "workflow_run_id":
                value = workflow_run_id_var.get()
            elif value is None and key == "module_run_id":
                value = module_run_id_var.get()
            elif value is None and key == "module_id":
                value = module_id_var.get()
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.addFilter(RedactionFilter())
    if settings.log_json:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
