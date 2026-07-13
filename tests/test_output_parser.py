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


def test_extract_json_from_nested_fence() -> None:
    parser = OutputParser()
    payload = {
        "module_id": "relationship_conversation_analysis",
        "module_version": "1.0.0",
        "executive_summary": "x",
        "findings": [
            {
                "id": "F001",
                "type": "observation",
                "summary": "nested",
            }
        ],
    }
    raw = f"```json\n{json.dumps(payload)}\n```\n\n## Report"
    data = parser.extract_json(raw)
    assert data["findings"][0]["id"] == "F001"


def test_extract_json_raises_when_fence_json_truncated() -> None:
    parser = OutputParser()
    raw = '```json\n{"module_id": "x", "findings": [{"id": "F001"\n```'
    with pytest.raises(OutputParseError, match="truncated"):
        parser.extract_json(raw)


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


def test_parse_input_coerces_bedrock_construct_aliases() -> None:
    parser = OutputParser()
    parsed = parser.parse_input(
        {
            "module_id": "relationship_conversation_analysis",
            "module_version": "1.0.0",
            "executive_summary": "Escalation with limited repair.",
            "constructs": [
                {
                    "id": "communication_pattern",
                    "summary": "Partners respond defensively to each other",
                }
            ],
            "relationships": [
                {
                    "source_id": "F001",
                    "target_id": "F002",
                    "type": "contributes_to",
                }
            ],
        }
    )

    assert parsed.constructs[0].type == "communication_pattern"
    assert parsed.constructs[0].label == "communication pattern"
    assert parsed.constructs[0].confidence == "exploratory"
    assert parsed.relationships[0].source_construct_id == "F001"
    assert parsed.relationships[0].target_construct_id == "F002"
    assert parsed.relationships[0].confidence == "exploratory"


def test_normalize_unknown_relationship_type_defaults() -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    output = parser.normalize(
        {
            "module_id": "relationship_conversation_analysis",
            "module_version": "1.0.0",
            "executive_summary": "x",
            "relationships": [
                {
                    "source_construct_id": "C001",
                    "target_construct_id": "C002",
                    "relationship_type": "reinforces",
                    "confidence": "moderate",
                }
            ],
        },
        module,
        "run-456",
    )
    assert output.relationships[0].relationship_type.value == "supports"


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [
        ("leads_to", "contributes_to"),
        ("causes", "contributes_to"),
        ("triggers", "escalates"),
        ("related_to", "co_occurs_with"),
        ("links", "co_occurs_with"),
        ("totally_made_up", "co_occurs_with"),
        ("Supports", "supports"),
        ("co-occurs-with", "co_occurs_with"),
    ],
)
def test_relationship_type_aliases_and_defaults(raw_type: str, expected: str) -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    output = parser.normalize(
        {
            "module_id": "relationship_conversation_analysis",
            "module_version": "1.0.0",
            "executive_summary": "x",
            "relationships": [
                {
                    "source_construct_id": "C001",
                    "target_construct_id": "C002",
                    "relationship_type": raw_type,
                    "confidence": "moderate",
                }
            ],
        },
        module,
        "run-alias",
    )
    assert output.relationships[0].relationship_type.value == expected


def test_parse_input_coerces_from_to_and_name_aliases() -> None:
    parser = OutputParser()
    parsed = parser.parse_input(
        {
            "module_id": "nvc_analysis",
            "module_version": "1.0.0",
            "executive_summary": "Needs vs strategies.",
            "constructs": [
                {
                    "name": "Autonomy need",
                    "category": "need",
                    "summary": "Desire for choice",
                }
            ],
            "relationships": [
                {
                    "from": "C001",
                    "to": "C002",
                    "relation": "supports",
                },
                {
                    # incomplete — dropped
                    "from": "C001",
                },
            ],
        }
    )

    assert parsed.constructs[0].label == "Autonomy need"
    assert parsed.constructs[0].type == "need"
    assert parsed.constructs[0].description == "Desire for choice"
    assert len(parsed.relationships) == 1
    assert parsed.relationships[0].source_construct_id == "C001"
    assert parsed.relationships[0].target_construct_id == "C002"
    assert parsed.relationships[0].relationship_type == "supports"


def test_normalize_rejects_invalid_finding_confidence() -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    with pytest.raises(OutputParseError, match="confidence"):
        parser.normalize(
            {
                "module_id": "relationship_conversation_analysis",
                "module_version": "1.0.0",
                "executive_summary": "x",
                "findings": [
                    {
                        "type": "observation",
                        "title": "t",
                        "summary": "s",
                        "confidence": "not_a_real_level",
                    }
                ],
            },
            module,
            "run-bad",
        )
