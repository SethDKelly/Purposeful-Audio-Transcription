import json
import logging

from backend.core.log_context import log_context_extra, module_run_id_var, request_id_var
from backend.core.logging_config import JsonLogFormatter


def test_json_log_formatter_includes_context_fields() -> None:
    token = request_id_var.set("req-1")
    module_token = module_run_id_var.set("modrun-1")
    try:
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Module run failed",
            args=(),
            exc_info=None,
        )
        record.event = "module.run.failed"
        record.error_type = "LLMError"
        record.module_id = "relationship_conversation_analysis"

        payload = json.loads(JsonLogFormatter().format(record))
        assert payload["request_id"] == "req-1"
        assert payload["module_run_id"] == "modrun-1"
        assert payload["module_id"] == "relationship_conversation_analysis"
        assert payload["error_type"] == "LLMError"
        assert payload["event"] == "module.run.failed"
    finally:
        module_run_id_var.reset(module_token)
        request_id_var.reset(token)


def test_log_context_extra_merges_overrides() -> None:
    extra = log_context_extra(error_type="ValidationError", module_id="nvc_analysis")
    assert extra["error_type"] == "ValidationError"
    assert extra["module_id"] == "nvc_analysis"
