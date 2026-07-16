import json
from pathlib import Path

import pytest

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import Confidence
from backend.services.module_output_validator import ModuleOutputValidator
from backend.services.output_parser import OutputParser
from backend.services.safety_validator import SafetyValidator

FIXTURES = Path(__file__).parent / "fixtures"


def _sample_output(module_id: str = "relationship_conversation_analysis"):
    registry = ModuleRegistry()
    module = registry.get(module_id)
    data = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    data["module_id"] = module.config.id
    data["module_version"] = module.config.version
    return (
        module,
        OutputParser().normalize(data, module, "run-123"),
        {f"Q{index:03d}" for index in range(1, 5)},
    )


def test_validator_accepts_valid_output() -> None:
    module, output, quote_ids = _sample_output()
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert result.is_valid
    # Sample fixture has empty constructs[]; soft warning expected.
    assert result.warnings
    assert result.construct_coverage is not None
    assert result.construct_coverage.missing


def test_validator_reports_full_construct_coverage() -> None:
    module, output, quote_ids = _sample_output()
    from backend.domain.enums import Confidence
    from backend.domain.finding import Construct

    output.constructs = [
        Construct(
            id="C001",
            type="interaction_cycle",
            label="Cycle",
            confidence=Confidence.OBSERVED,
            evidence_quote_ids=["Q001"],
        ),
        Construct(
            id="C002",
            type="escalation_point",
            label="Escalation",
            confidence=Confidence.OBSERVED,
            evidence_quote_ids=["Q002"],
        ),
        Construct(
            id="C003",
            type="repair_attempt",
            label="Repair",
            confidence=Confidence.OBSERVED,
            evidence_quote_ids=["Q004"],
        ),
        Construct(
            id="C004",
            type="emotion",
            label="Emotion",
            confidence=Confidence.OBSERVED,
            evidence_quote_ids=["Q001"],
        ),
    ]
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert result.is_valid
    assert not result.warnings
    assert result.construct_coverage is not None
    assert result.construct_coverage.missing == []
    assert result.construct_coverage.coverage_rate == 1.0


def test_validator_counts_finding_types_toward_coverage() -> None:
    module, output, quote_ids = _sample_output()
    # Findings already include emotion, repair_attempt, interaction_cycle.
    # Still missing escalation_point from expected_constructs.
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert result.is_valid
    assert result.construct_coverage is not None
    assert "escalation_point" in result.construct_coverage.missing
    assert "emotion" in result.construct_coverage.found
    assert "repair_attempt" in result.construct_coverage.found


def test_validator_rejects_unknown_quote_id() -> None:
    module, output, quote_ids = _sample_output()
    output.findings[0].evidence_quote_ids = ["Q999"]
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert not result.is_valid
    assert any("Q999" in error for error in result.errors)


def test_validator_rejects_confidence_above_ceiling() -> None:
    module, output, quote_ids = _sample_output("nvc_analysis")
    output.findings[0].confidence = Confidence.HIGH
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert not result.is_valid


def test_validator_requires_alternative_explanations_for_inferred_findings() -> None:
    module, output, quote_ids = _sample_output()
    output.findings[2].alternative_explanations = []
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert not result.is_valid
    assert any("alternative_explanations" in error for error in result.errors)


def test_safety_validator_flags_diagnosis_language() -> None:
    module, output, _ = _sample_output()
    output.executive_summary = "Person A is diagnosed with narcissistic personality disorder."
    result = SafetyValidator().validate(output)
    assert not result.is_safe


def test_safety_validator_accepts_clean_output() -> None:
    _, output, _ = _sample_output()
    result = SafetyValidator().validate(output)
    assert result.is_safe


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("executive_summary", "This relationship will fail within a year."),
        ("executive_summary", "Person A should take medication for this conflict."),
        ("executive_summary", "Person B is guilty of emotional abuse."),
    ],
)
def test_safety_validator_flags_forbidden_patterns(field_name: str, value: str) -> None:
    _, output, _ = _sample_output()
    setattr(output, field_name, value)
    result = SafetyValidator().validate(output)
    assert not result.is_safe


def test_safety_validator_warns_on_intent_stated_as_fact() -> None:
    _, output, _ = _sample_output()
    output.executive_summary = "Person B clearly intended to hurt Person A."
    result = SafetyValidator().validate(output)
    assert result.is_safe
    assert any("Intent stated as fact" in flag for flag in result.flags)


def test_safety_validator_flags_abuse_label_without_evidence() -> None:
    _, output, _ = _sample_output()
    output.executive_summary = "Person B is abusive."
    for finding in output.findings:
        finding.evidence_quote_ids = []
        finding.confidence = Confidence.LOW
    result = SafetyValidator().validate(output)
    assert not result.is_safe
