"""Validate synthesis reports against business rules."""

from dataclasses import dataclass, field

from backend.domain.synthesis import SynthesisReport


@dataclass
class SynthesisValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


class SynthesisOutputValidator:
    def validate(
        self,
        report: SynthesisReport,
        allowed_quote_ids: set[str],
    ) -> SynthesisValidationResult:
        result = SynthesisValidationResult()

        if not report.executive_summary.strip():
            result.errors.append("executive_summary is required")

        all_findings = (
            report.high_confidence_findings
            + report.moderate_confidence_findings
            + report.exploratory_hypotheses
        )
        for finding in all_findings:
            for quote_id in finding.evidence_quote_ids:
                if quote_id not in allowed_quote_ids:
                    result.errors.append(
                        f"finding {finding.id} references unsupported quote ID {quote_id}"
                    )

        if not report.convergence and not report.divergence and len(all_findings) > 1:
            result.warnings.append(
                "No convergence or divergence statements were produced across modules"
            )

        return result


synthesis_output_validator = SynthesisOutputValidator()
