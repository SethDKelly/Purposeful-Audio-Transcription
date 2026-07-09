"""Validate structured module output against business rules."""

from dataclasses import dataclass, field

from backend.core.module_registry import AnalysisModule
from backend.domain.enums import CONFIDENCE_RANK, Confidence
from backend.schemas.module_output_v1 import ModuleRunOutput

_INFERRED_CONFIDENCES = {
    Confidence.HIGH,
    Confidence.MODERATE,
    Confidence.LOW,
    Confidence.EXPLORATORY,
}


@dataclass
class ModuleOutputValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


class ModuleOutputValidator:
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

        return result

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
                f"exceeds module ceiling"
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
