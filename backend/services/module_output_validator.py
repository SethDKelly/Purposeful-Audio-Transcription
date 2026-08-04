"""Validate structured module output against business rules."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from backend.core.module_registry import AnalysisModule
from backend.core.ontology_registry import OntologyRegistry, ontology_registry
from backend.domain.enums import CONFIDENCE_RANK, Confidence
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.evidence_precision import looks_like_paragraph
from config.settings import settings

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
        quote_texts: dict[str, str] | None = None,
    ) -> ModuleOutputValidationResult:
        result = ModuleOutputValidationResult()
        config = module.config
        texts = quote_texts or {}

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
                quote_texts=texts,
            )

        for construct in output.constructs:
            if construct.evidence_quote_ids:
                self._validate_quote_ids(
                    construct.evidence_quote_ids,
                    valid_quote_ids,
                    f"construct {construct.id}",
                    result,
                )
                self._validate_evidence_precision(
                    construct.evidence_quote_ids,
                    f"construct {construct.id}",
                    result,
                    quote_texts=texts,
                    enforce_max_items=False,
                )
            if construct.confidence not in {
                Confidence.OBSERVED,
                Confidence.INSUFFICIENT_EVIDENCE,
            } and CONFIDENCE_RANK[construct.confidence] > ceiling_rank:
                result.errors.append(
                    f"construct {construct.id} confidence {construct.confidence.value} "
                    f"exceeds module ceiling {config.confidence_ceiling.value}"
                )

        for relationship in output.relationships:
            self._validate_relationship(
                relationship,
                valid_quote_ids,
                ceiling_rank,
                result,
                quote_texts=texts,
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
        quote_texts: dict[str, str] | None = None,
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
            self._validate_evidence_precision(
                finding.evidence_quote_ids,
                f"finding {finding.id}",
                result,
                quote_texts=quote_texts or {},
                enforce_max_items=True,
            )

        if (
            finding.confidence in _INFERRED_CONFIDENCES
            and not finding.alternative_explanations
        ):
            result.errors.append(
                f"finding {finding.id} with confidence {finding.confidence.value} "
                "must include alternative_explanations"
            )

    def _validate_relationship(
        self,
        relationship,
        valid_quote_ids: set[str],
        ceiling_rank: int,
        result: ModuleOutputValidationResult,
        *,
        quote_texts: dict[str, str] | None = None,
    ) -> None:
        context = f"relationship {relationship.id}"
        if relationship.confidence not in {
            Confidence.OBSERVED,
            Confidence.INSUFFICIENT_EVIDENCE,
        } and CONFIDENCE_RANK[relationship.confidence] > ceiling_rank:
            result.errors.append(
                f"{context} confidence {relationship.confidence.value} "
                "exceeds module ceiling"
            )

        if relationship.evidence_quote_ids:
            self._validate_quote_ids(
                relationship.evidence_quote_ids,
                valid_quote_ids,
                context,
                result,
            )
            self._validate_evidence_precision(
                relationship.evidence_quote_ids,
                context,
                result,
                quote_texts=quote_texts or {},
                enforce_max_items=False,
            )

        rationale = (relationship.rationale or "").strip()
        if not rationale:
            result.warnings.append(f"{context} should include a rationale")
        if not relationship.evidence_quote_ids and not rationale:
            result.warnings.append(
                f"{context} has no evidence_quote_ids and no rationale"
            )

        if (
            relationship.confidence in _INFERRED_CONFIDENCES
            and not relationship.alternative_explanations
        ):
            result.warnings.append(
                f"{context} with confidence {relationship.confidence.value} "
                "should include alternative_explanations"
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

    def _validate_evidence_precision(
        self,
        quote_ids: list[str],
        context: str,
        result: ModuleOutputValidationResult,
        *,
        quote_texts: dict[str, str],
        enforce_max_items: bool,
    ) -> None:
        max_items = settings.evidence_max_items_per_finding
        if enforce_max_items and len(quote_ids) > max_items:
            result.errors.append(
                f"{context} cites {len(quote_ids)} evidence items "
                f"(max {max_items}); prefer the smallest useful spans"
            )

        if not quote_texts:
            return

        for quote_id in quote_ids:
            text = quote_texts.get(quote_id)
            if text is None:
                continue
            length = len(text)
            if length > settings.evidence_hard_max_chars:
                result.errors.append(
                    f"{context} evidence {quote_id} is {length} chars "
                    f"(hard max {settings.evidence_hard_max_chars}); "
                    "cite a shorter turn or sentence-level span"
                )
            elif length > settings.evidence_warning_threshold_chars:
                result.warnings.append(
                    f"{context} evidence {quote_id} is {length} chars "
                    f"(warning threshold {settings.evidence_warning_threshold_chars})"
                )
            if looks_like_paragraph(text):
                result.warnings.append(
                    f"{context} evidence {quote_id} looks like paragraph-length "
                    "evidence; prefer an atomic quote or short exchange"
                )


module_output_validator = ModuleOutputValidator()
