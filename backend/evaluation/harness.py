"""Score module outputs against golden assertions and release gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from backend.evaluation.claims import ForbiddenClaimScorer, flatten_output_text
from tests.helpers.golden_transcripts import (
    GoldenFixture,
    collect_constructs,
    collect_findings,
    contains_signal,
    cites_any,
    load_golden_fixture_by_id,
    validate_evidence_quote_ids,
)

HIGH_CONFIDENCE = frozenset({"high", "observed", "confirmed"})


@dataclass
class EvalGateConfig:
    min_required_signal_hit_rate: float = 0.5
    min_evidence_coverage_rate: float = 0.5
    max_forbidden_claim_count: int = 0
    max_confidence_ceiling_violations: int = 0
    require_schema_valid: bool = True


@dataclass
class ModuleEvalResult:
    fixture_id: str
    workflow_id: str | None
    module_id: str
    module_version: str | None = None
    model_id: str | None = None
    schema_valid: bool = True
    finding_count: int = 0
    construct_count: int = 0
    evidence_coverage_rate: float = 0.0
    required_signal_hit_rate: float = 0.0
    forbidden_claim_count: int = 0
    unsupported_claim_count: int = 0
    confidence_ceiling_violations: int = 0
    construct_coverage_hit: bool = False
    gate_passed: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload


def evaluate_module_output(
    *,
    fixture: GoldenFixture,
    module_id: str,
    module_output: dict[str, Any],
    valid_quote_ids: set[str] | None = None,
    confidence_ceiling: str | None = None,
    module_version: str | None = None,
    model_id: str | None = None,
    workflow_id: str | None = None,
    gates: EvalGateConfig | None = None,
) -> ModuleEvalResult:
    gates = gates or EvalGateConfig()
    assertions = fixture.assertions
    findings = collect_findings(module_output)
    constructs = collect_constructs(module_output)

    schema_valid = True
    schema_errors: list[str] = []
    try:
        if valid_quote_ids is not None:
            validate_evidence_quote_ids(module_output, valid_quote_ids)
    except AssertionError as exc:
        schema_valid = False
        schema_errors.append(str(exc))

    required_signals = assertions.get("required_signals") or []
    hits = 0
    for signal in required_signals:
        signal_type = str(signal.get("type") or "")
        refs = signal.get("must_reference_any") or []
        if contains_signal(module_output, signal_type) and (
            not refs or cites_any(module_output, refs)
        ):
            hits += 1
    signal_rate = (hits / len(required_signals)) if required_signals else 1.0

    findings_with_evidence = sum(1 for f in findings if f.get("evidence_quote_ids"))
    evidence_rate = (findings_with_evidence / len(findings)) if findings else 1.0

    claim_score = ForbiddenClaimScorer().score_module_output(module_output)

    unsupported = 0
    for finding in findings:
        if not finding.get("evidence_quote_ids"):
            conf = str(finding.get("confidence") or "").lower()
            if conf in HIGH_CONFIDENCE:
                unsupported += 1

    ceiling_violations = 0
    if confidence_ceiling:
        order = {"low": 0, "moderate": 1, "high": 2, "observed": 2, "confirmed": 2}
        ceiling_rank = order.get(confidence_ceiling.lower(), 1)
        for finding in findings:
            conf = str(finding.get("confidence") or "moderate").lower()
            if order.get(conf, 1) > ceiling_rank:
                ceiling_violations += 1

    expected_constructs = assertions.get("expected_construct_types") or {}
    include_any = expected_constructs.get("include_any") or []
    construct_types = {
        str(c.get("type") or "").lower() for c in constructs if isinstance(c, dict)
    }
    construct_hit = True
    if include_any:
        construct_hit = any(
            any(token.lower() in ctype for ctype in construct_types)
            for token in include_any
        )
    min_total = int(expected_constructs.get("minimum_total") or 0)
    if min_total and len(constructs) < min_total:
        construct_hit = False

    result = ModuleEvalResult(
        fixture_id=fixture.fixture_id,
        workflow_id=workflow_id,
        module_id=module_id,
        module_version=module_version,
        model_id=model_id,
        schema_valid=schema_valid,
        finding_count=len(findings),
        construct_count=len(constructs),
        evidence_coverage_rate=round(evidence_rate, 4),
        required_signal_hit_rate=round(signal_rate, 4),
        forbidden_claim_count=claim_score.forbidden_claim_count,
        unsupported_claim_count=unsupported,
        confidence_ceiling_violations=ceiling_violations,
        construct_coverage_hit=construct_hit,
        details={
            "schema_errors": schema_errors,
            "forbidden": claim_score.to_dict(),
            "text_length": len(flatten_output_text(module_output)),
        },
    )
    result.gate_passed = _passes_gates(result, gates)
    return result


def _passes_gates(result: ModuleEvalResult, gates: EvalGateConfig) -> bool:
    if gates.require_schema_valid and not result.schema_valid:
        return False
    if result.required_signal_hit_rate < gates.min_required_signal_hit_rate:
        return False
    if result.evidence_coverage_rate < gates.min_evidence_coverage_rate:
        return False
    if result.forbidden_claim_count > gates.max_forbidden_claim_count:
        return False
    if result.confidence_ceiling_violations > gates.max_confidence_ceiling_violations:
        return False
    return True


class GoldenEvalHarness:
    """Run selected fixtures/modules and collect structured metrics."""

    def __init__(self, gates: EvalGateConfig | None = None) -> None:
        self.gates = gates or EvalGateConfig()

    def score_output(
        self,
        *,
        fixture_id: str,
        module_id: str,
        module_output: dict[str, Any],
        valid_quote_ids: set[str] | None = None,
        confidence_ceiling: str | None = None,
        module_version: str | None = None,
        model_id: str | None = None,
        workflow_id: str | None = None,
    ) -> ModuleEvalResult:
        fixture = load_golden_fixture_by_id(fixture_id)
        return evaluate_module_output(
            fixture=fixture,
            module_id=module_id,
            module_output=module_output,
            valid_quote_ids=valid_quote_ids,
            confidence_ceiling=confidence_ceiling,
            module_version=module_version,
            model_id=model_id,
            workflow_id=workflow_id,
            gates=self.gates,
        )


class ModuleVersionComparer:
    """Compare two scored module outputs on the same fixture."""

    def compare(
        self,
        *,
        baseline: ModuleEvalResult,
        candidate: ModuleEvalResult,
    ) -> dict[str, Any]:
        metrics = [
            "schema_valid",
            "required_signal_hit_rate",
            "evidence_coverage_rate",
            "construct_count",
            "forbidden_claim_count",
            "confidence_ceiling_violations",
            "unsupported_claim_count",
        ]
        deltas: dict[str, Any] = {}
        for key in metrics:
            left = getattr(baseline, key)
            right = getattr(candidate, key)
            if isinstance(left, bool):
                deltas[key] = {"baseline": left, "candidate": right, "regressed": left and not right}
            elif isinstance(left, (int, float)):
                deltas[key] = {
                    "baseline": left,
                    "candidate": right,
                    "delta": right - left,
                }
        regressions = []
        if baseline.schema_valid and not candidate.schema_valid:
            regressions.append("schema_valid")
        if candidate.required_signal_hit_rate < baseline.required_signal_hit_rate:
            regressions.append("required_signal_hit_rate")
        if candidate.forbidden_claim_count > baseline.forbidden_claim_count:
            regressions.append("forbidden_claim_count")
        return {
            "fixture_id": baseline.fixture_id,
            "module_id": baseline.module_id,
            "baseline_version": baseline.module_version,
            "candidate_version": candidate.module_version,
            "deltas": deltas,
            "regressions": regressions,
            "candidate_better": not regressions
            and candidate.required_signal_hit_rate >= baseline.required_signal_hit_rate,
        }


DEFAULT_RESULTS_DIR = Path("tests/golden_results")
