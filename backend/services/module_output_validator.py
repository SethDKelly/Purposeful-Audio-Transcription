"""Validate structured module output against business rules."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from backend.core.module_registry import AnalysisModule
from backend.core.ontology_registry import OntologyRegistry, ontology_registry
from backend.domain.enums import CONFIDENCE_RANK, Confidence
from backend.schemas.module_output_v1 import ModuleRunOutput

logger = logging.getLogger(__name__)

_INFERRED_CONFIDENCES = {
    Confidence.HIGH,
    Confidence.MODERATE,
    Confidence.LOW,
    Confidence.EXPLORATORY,
}


@dataclass
class ConstructCoverage:
    expected: list[str] = field(default_factory=list)
    found: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    construct_count: int = 0
    min_constructs: int = 0

    @property
    def coverage_rate(self) -> float:
        if not self.expected:
            return 1.0
        return len(self.found) / len(self.expected)

    def as_dict(self) -> dict:
        return {
            "expected": list(self.expected),
            "found": list(self.found),
            "missing": list(self.missing),
            "construct_count": self.construct_count,
            "min_constructs": self.min_constructs,
            "coverage_rate": round(self.coverage_rate, 3),
        }


@dataclass
class ModuleOutputValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    construct_coverage: ConstructCoverage | None = None

    @property
    def is_valid(self) -> bool:
        return not self.errors


class ModuleOutputValidator:
    def __init__(self, ontology: OntologyRegistry | None = None) -> None:
        self._ontology = ontology or ontology_registry

    def validate(
        self,
        output: ModuleRunOutput,
        module: AnalysisModule,
        valid_quote_ids: set[str],
        *,
        require_evidence: bool = True,
    ) -> ModuleOutputValidationResult:
        result = ModuleOutputValidationResult()
        config = module.config

        if output.module_id != config.id:
            result.errors.append(
                f"module_id mismatch: expected {config.id}, got {output.module_id}"
            )
        if output.module_version != config.version:
            result.errors.append(
                "module_version mismatch: "
                f"expected {config.version}, got {output.module_version}"
            )
        if not output.executive_summary.strip():
            result.errors.append("executive_summary is required")

        ceiling_rank = CONFIDENCE_RANK[config.confidence_ceiling]
        for finding in output.findings:
            self._validate_finding(
                finding,
                valid_quote_ids,
                ceiling_rank,
                result,
                require_evidence=require_evidence,
            )

        for construct in output.constructs:
            if construct.evidence_quote_ids:
                self._validate_quote_ids(
                    construct.evidence_quote_ids,
                    valid_quote_ids,
                    f"construct {construct.id}",
                    result,
                )
            if construct.confidence not in {
                Confidence.OBSERVED,
                Confidence.INSUFFICIENT_EVIDENCE,
            } and CONFIDENCE_RANK[construct.confidence] > ceiling_rank:
                result.errors.append(
                    f"construct {construct.id} confidence {construct.confidence.value} "
                    f"exceeds module ceiling {config.confidence_ceiling.value}"
                )

        result.construct_coverage = self._assess_construct_coverage(output, module)
        result.warnings.extend(
            self._coverage_warnings(result.construct_coverage, module.config.id)
        )
        return result

    def _assess_construct_coverage(
        self,
        output: ModuleRunOutput,
        module: AnalysisModule,
    ) -> ConstructCoverage:
        expected_raw = list(module.config.expected_constructs or [])
        expected: list[str] = []
        for item in expected_raw:
            resolved = self._ontology.resolve_construct(item) or item
            if resolved not in expected:
                expected.append(resolved)

        emitted: set[str] = set()
        for construct in output.constructs:
            resolved = self._ontology.resolve_construct(construct.type) or construct.type
            emitted.add(resolved)
        for finding in output.findings:
            finding_type = getattr(finding.type, "value", str(finding.type))
            resolved = self._ontology.resolve_construct(finding_type) or finding_type
            emitted.add(resolved)

        found = [item for item in expected if item in emitted]
        missing = [item for item in expected if item not in emitted]
        min_constructs = module.config.min_constructs
        if min_constructs is None:
            min_constructs = 1 if expected else 0

        return ConstructCoverage(
            expected=expected,
            found=found,
            missing=missing,
            construct_count=len(output.constructs),
            min_constructs=min_constructs,
        )

    def _coverage_warnings(
        self,
        coverage: ConstructCoverage,
        module_id: str,
    ) -> list[str]:
        warnings: list[str] = []
        if coverage.missing:
            warnings.append(
                f"Weak construct coverage for {module_id}: missing "
                f"{', '.join(coverage.missing)} "
                f"(found {len(coverage.found)}/{len(coverage.expected)}, "
                f"rate={coverage.coverage_rate:.2f})"
            )
        if coverage.construct_count < coverage.min_constructs:
            warnings.append(
                f"Construct count below minimum for {module_id}: "
                f"{coverage.construct_count} < {coverage.min_constructs}"
            )
        if warnings:
            logger.info(
                "Module construct coverage warning",
                extra={
                    "event": "module.construct_coverage",
                    "module_id": module_id,
                    "coverage": coverage.as_dict(),
                    "warnings": warnings,
                },
            )
        return warnings

    def _validate_finding(
        self,
        finding,
        valid_quote_ids: set[str],
        ceiling_rank: int,
        result: ModuleOutputValidationResult,
        *,
        require_evidence: bool = True,
    ) -> None:
        if not finding.title.strip() or not finding.summary.strip():
            result.errors.append(f"finding {finding.id} must include title and summary")

        if finding.confidence not in {
            Confidence.OBSERVED,
            Confidence.INSUFFICIENT_EVIDENCE,
        } and CONFIDENCE_RANK[finding.confidence] > ceiling_rank:
            result.errors.append(
                f"finding {finding.id} confidence {finding.confidence.value} "
                "exceeds module ceiling"
            )

        is_limitation_only = finding.type.value == "uncertainty" and not finding.evidence_quote_ids
        if require_evidence and not finding.evidence_quote_ids and not is_limitation_only:
            result.errors.append(
                f"finding {finding.id} must include at least one evidence_quote_id"
            )

        if finding.evidence_quote_ids:
            self._validate_quote_ids(
                finding.evidence_quote_ids,
                valid_quote_ids,
                f"finding {finding.id}",
                result,
            )

        if (
            finding.confidence in _INFERRED_CONFIDENCES
            and not finding.alternative_explanations
        ):
            result.errors.append(
                f"finding {finding.id} with confidence {finding.confidence.value} "
                "must include alternative_explanations"
            )

    def _validate_quote_ids(
        self,
        quote_ids: list[str],
        valid_quote_ids: set[str],
        context: str,
        result: ModuleOutputValidationResult,
    ) -> None:
        for quote_id in quote_ids:
            if quote_id not in valid_quote_ids:
                result.errors.append(f"{context} references unknown quote ID {quote_id}")


module_output_validator = ModuleOutputValidator()
