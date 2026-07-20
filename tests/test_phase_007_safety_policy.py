"""Phase 007 — safety policy and non-diagnostic enforcement."""

from __future__ import annotations

from pathlib import Path

from backend.domain.enums import Confidence
from backend.services.safety_policy import get_safety_policy, reload_safety_policy
from backend.services.safety_risk_scanner import safety_risk_scanner
from backend.services.safety_validator import SafetyValidator
from backend.services.module_output_validator import ModuleOutputValidator
from backend.services.output_parser import OutputParser
from backend.core.module_registry import ModuleRegistry
import json

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def _sample_output():
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    data = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    data["module_id"] = module.config.id
    data["module_version"] = module.config.version
    return module, OutputParser().normalize(data, module, "run-safety")


def test_phase_007_docs_and_policy_exist() -> None:
    phase = (
        ROOT
        / "docs"
        / "planning"
        / "phases"
        / "007_v2_1_safety_policy_and_non_diagnostic_enforcement.md"
    )
    policy = ROOT / "config" / "safety_policy.yaml"
    product = ROOT / "docs" / "product" / "safety_aware_report_mode.md"
    assert phase.is_file()
    assert policy.is_file()
    assert product.is_file()
    shared = (ROOT / "config" / "framework" / "shared_instructions.md").read_text(
        encoding="utf-8"
    )
    assert "mutualize" in shared.lower() or "mutualizing" in shared.lower()


def test_safety_policy_defaults_loaded() -> None:
    reload_safety_policy()
    policy = get_safety_policy()
    assert policy.elevated_risk_triggers_safety_mode is True
    assert policy.high_risk_triggers_safety_mode is True
    assert "exploratory_psychological_formulation" in policy.suppress_modules
    assert "trauma_informed_communication" in policy.modify_modules
    assert policy.should_enable_safety_mode("elevated") is True
    assert policy.should_enable_safety_mode("high") is True
    assert policy.should_enable_safety_mode("none") is False


def test_elevated_risk_recommends_safety_mode() -> None:
    scan = safety_risk_scanner.scan(
        "Person A: Do what I say or else.\nPerson B: Please stop controlling me."
    )
    assert scan.risk_level == "elevated"
    assert scan.safety_mode_recommended is True


def test_high_risk_recommends_safety_mode() -> None:
    scan = safety_risk_scanner.scan("Person A: I will kill you if you leave.")
    assert scan.risk_level == "high"
    assert scan.safety_mode_recommended is True


def test_ordinary_conflict_false_positive() -> None:
    scan = safety_risk_scanner.scan(
        "Person A: I was frustrated about dinner.\nPerson B: Let's talk tomorrow."
    )
    assert scan.risk_level == "none"
    assert scan.safety_mode_recommended is False


def test_validator_blocks_definitive_diagnosis() -> None:
    _, output = _sample_output()
    output.executive_summary = "Person A has narcissistic personality disorder."
    result = SafetyValidator().validate(output)
    assert not result.is_safe


def test_validator_blocks_abuse_determination_even_with_evidence() -> None:
    _, output = _sample_output()
    output.executive_summary = "Person B is abusive."
    for finding in output.findings:
        finding.evidence_quote_ids = ["Q001"]
        finding.confidence = Confidence.OBSERVED
    result = SafetyValidator().validate(output)
    assert not result.is_safe


def test_validator_blocks_mutualizing_in_safety_mode() -> None:
    _, output = _sample_output()
    output.executive_summary = "Both are equally responsible for the threats."
    result = SafetyValidator().validate(output, safety_mode=True)
    assert not result.is_safe
    assert any("Mutualizing" in v for v in result.violations)


def test_validator_ignores_quoted_transcript_claim_language() -> None:
    _, output = _sample_output()
    # Quoted citation of a threat should not be treated as a model diagnosis/adjudication.
    output.executive_summary = (
        'Speaker said "I will kill you" in the transcript; treat as a quoted cue only.'
    )
    result = SafetyValidator().validate(output, safety_mode=True)
    assert result.is_safe


def test_validator_flags_manipulation_determination() -> None:
    _, output = _sample_output()
    output.recommendations = ["Person A intentionally manipulates Person B."]
    result = SafetyValidator().validate(output)
    assert not result.is_safe


def test_module_output_still_validates_clean_sample() -> None:
    module, output = _sample_output()
    quote_ids = {f"Q{i:03d}" for i in range(1, 5)}
    result = ModuleOutputValidator().validate(output, module, quote_ids)
    assert result.is_valid
    safety = SafetyValidator().validate(output)
    assert safety.is_safe
