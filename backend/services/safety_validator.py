"""Safety checks for module analysis output."""

import re
from dataclasses import dataclass, field

from backend.domain.synthesis import SynthesisReport
from backend.schemas.module_output_v1 import ModuleRunOutput

_DIAGNOSIS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(diagnosed with|diagnosis of|has ptsd|has adhd|narcissist|narcissistic personality)\b",
        r"\b(borderline personality|bipolar disorder|schizophreni[ac])\b",
        r"\b(mentally ill|psychopath|sociopath)\b",
    )
]

_ABUSE_ASSERTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(is abusive|was abusive|abuser)\b",
        r"\b(is a narcissist|is manipulative)\b",
    )
]

_OUTCOME_PREDICTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(will divorce|will break up|relationship will fail|will leave you)\b",
        r"\b(destined to fail|no future together)\b",
    )
]

_LEGAL_MEDICAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(illegal|guilty of|medical diagnosis|prescribe|should take medication)\b",
        r"\b(subpoena|court order|restraining order should be)\b",
    )
]

_INTENT_AS_FACT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bclearly intended to hurt\b",
        r"\bdefinitely meant to\b",
        r"\btheir true intention was\b",
    )
]


@dataclass
class SafetyValidationResult:
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return not self.violations

    @property
    def flags(self) -> list[str]:
        return self.violations + self.warnings


class SafetyValidator:
    def validate(self, output: ModuleRunOutput) -> SafetyValidationResult:
        result = SafetyValidationResult()
        texts = _collect_texts(output)

        for text in texts:
            self._check_patterns(
                text,
                _DIAGNOSIS_PATTERNS,
                "Diagnostic or clinical labeling language detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _OUTCOME_PREDICTION_PATTERNS,
                "Relationship outcome prediction detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _LEGAL_MEDICAL_PATTERNS,
                "Legal or medical determination language detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _INTENT_AS_FACT_PATTERNS,
                "Intent stated as fact without qualification",
                result.warnings,
            )
            self._check_abuse_assertions(text, output, result)

        return result

    def validate_synthesis(self, report: SynthesisReport) -> SafetyValidationResult:
        result = SafetyValidationResult()
        texts = _collect_synthesis_texts(report)

        for text in texts:
            self._check_patterns(
                text,
                _DIAGNOSIS_PATTERNS,
                "Diagnostic or clinical labeling language detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _OUTCOME_PREDICTION_PATTERNS,
                "Relationship outcome prediction detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _LEGAL_MEDICAL_PATTERNS,
                "Legal or medical determination language detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _INTENT_AS_FACT_PATTERNS,
                "Intent stated as fact without qualification",
                result.warnings,
            )

        return result

    def _check_patterns(
        self,
        text: str,
        patterns: list[re.Pattern[str]],
        message: str,
        bucket: list[str],
    ) -> None:
        for pattern in patterns:
            if pattern.search(text) and message not in bucket:
                bucket.append(message)

    def _check_abuse_assertions(
        self,
        text: str,
        output: ModuleRunOutput,
        result: SafetyValidationResult,
    ) -> None:
        for pattern in _ABUSE_ASSERTION_PATTERNS:
            if not pattern.search(text):
                continue

            has_strong_evidence = any(
                finding.evidence_quote_ids
                and finding.confidence.value in {"observed", "high"}
                for finding in output.findings
                if pattern.search(f"{finding.title} {finding.summary}")
            )
            message = "Strong character or abuse labeling without sufficient evidence"
            if not has_strong_evidence and message not in result.violations:
                result.violations.append(message)


def _collect_texts(output: ModuleRunOutput) -> list[str]:
    texts = [output.executive_summary, output.raw_markdown_report]
    texts.extend(finding.title for finding in output.findings)
    texts.extend(finding.summary for finding in output.findings)
    texts.extend(output.recommendations)
    return [text for text in texts if text]


def _collect_synthesis_texts(report: SynthesisReport) -> list[str]:
    texts = [report.executive_summary]
    texts.extend(report.convergence)
    texts.extend(report.divergence)
    texts.extend(report.integrated_model)
    texts.extend(report.interventions)
    texts.extend(report.outstanding_questions)
    texts.extend(report.limitations)

    for finding in (
        report.high_confidence_findings
        + report.moderate_confidence_findings
        + report.exploratory_hypotheses
    ):
        texts.append(finding.title)
        texts.append(finding.summary)

    return [text for text in texts if text]


safety_validator = SafetyValidator()
