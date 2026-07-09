import json
from pathlib import Path

import pytest

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import Confidence
from backend.services.output_parser import OutputParseError, OutputParser

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_json_from_fence() -> None:
    parser = OutputParser()
    payload = '{"module_id": "nvc_analysis", "module_version": "1.0.0", "executive_summary": "x"}'
    raw = f"Here is the analysis:\n\n```json\n{payload}\n```\n\n## Report"
    data = parser.extract_json(raw)
    assert data["module_id"] == "nvc_analysis"


def test_extract_json_from_bare_object() -> None:
    parser = OutputParser()
    raw = 'Some text before {"module_id": "systems_analysis", "executive_summary": "x", "module_version": "1.0.0"} after'
    data = parser.extract_json(raw)
    assert data["module_id"] == "systems_analysis"


def test_extract_json_raises_when_missing() -> None:
    parser = OutputParser()
    with pytest.raises(OutputParseError):
        parser.extract_json("No structured output here.")


def test_normalize_sample_fixture() -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    data = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))

    output = parser.normalize(data, module, "run-123")

    assert output.module_id == "relationship_conversation_analysis"
    assert len(output.findings) == 3
    assert output.findings[0].module_run_id == "run-123"
    assert output.findings[2].confidence == Confidence.MODERATE
