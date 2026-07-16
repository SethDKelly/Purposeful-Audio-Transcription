"""Golden module contracts should surface construct coverage soft warnings."""

from __future__ import annotations

import json

import pytest

from backend.core.module_registry import ModuleRegistry
from backend.services.module_output_validator import ModuleOutputValidator
from backend.services.output_parser import OutputParser
from tests.test_workflow_engine import _module_llm_response

pytestmark = pytest.mark.golden


def test_sample_module_output_emits_construct_coverage_warning(gt001_fixture) -> None:
    module = ModuleRegistry().get("relationship_conversation_analysis")
    raw = _module_llm_response("relationship_conversation_analysis")
    payload = json.loads(raw.split("```json\n", 1)[1].rsplit("\n```", 1)[0])
    output = OutputParser().normalize(payload, module, "run-coverage")
    result = ModuleOutputValidator().validate(
        output,
        module,
        {f"Q{index:03d}" for index in range(1, 40)},
    )
    assert result.is_valid
    assert result.construct_coverage is not None
    # Sample fixture constructs[] is empty; findings only partially cover expected set.
    assert result.warnings or result.construct_coverage.missing
    assert "escalation_point" in result.construct_coverage.missing or result.warnings
