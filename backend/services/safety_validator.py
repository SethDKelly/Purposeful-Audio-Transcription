"""Safety checks for module analysis output (phase 007 hardened)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.domain.enums import Confidence
from backend.domain.synthesis import SynthesisReport
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.safety_policy import get_safety_policy

_DIAGNOSIS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(diagnosed with|diagnosis of|has ptsd|has adhd|narcissist|narcissistic personality)\b",
        r"\b(borderline personality|bipolar disorder|schizophreni[ac])\b",
        r"\b(mentally ill|psychopath|sociopath)\b",
        r"\b(narcissistic personality disorder|borderline personality disorder|has npd|has bpd)\b",
        r"\b(is a narcissist|clearly narcissistic|definite narcissism)\b",
    )
]

_ABUSE_ASSERTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(is abusive|was abusive|is an abuser|this is abuse)\b",
        r"\b(is a narcissist|is manipulative)\b",
        r"\b(is coercive control|engages in coercive control|definitely controlling)\b",
        r"\b(intentionally manipulat\w*|deliberately manipulat\w*)\b",
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

_TRAUMA_ATTACHMENT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(has childhood trauma|was traumatized as a child)\b",
        r"\b(is securely attached|is avoidantly attached|has anxious attachment)\b",
        r"\b(attachment style is)\b",
    )
]

_MUTUALIZING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bboth\b.{0,40}\bequally responsible\b",
        r"\b(equally at fault|mutual abuse)\b",
        r"\b(both need to (compromise|reconcile|meet in the middle))\b",
        r"\b(recommend(ed|ing)? reconcil)\b",
        r"\b(you should stay and work it out)\b",
        r"\b(shared responsibility for (the )?(threats|violence|coercion))\b",
    )
]

_QUOTE_SPAN = re.compile(r"[\"“”']([^\"“”']{3,})[\"“”']")
_CONFIDENCE_RANK = {
    Confidence.OBSERVED: 5,
    Confidence.HIGH: 4,
    Confidence.MODERATE: 3,
    Confidence.LOW: 2,
    Confidence.EXPLORATORY: 1,
    Confidence.INSUFFICIENT_EVIDENCE: 0,
}


@dataclass
class SafetyValidationResult:
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    downgraded_finding_ids: list[str] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return not self.violations

    @property
    def flags(self) -> list[str]:
        return self.violations + self.warnings


class SafetyValidator:
    def validate(
        self,
        output: ModuleRunOutput,
        *,
        safety_mode: bool = False,
    ) -> SafetyValidationResult:
        result = SafetyValidationResult()
        texts = _collect_claim_texts(output)

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
                result.warnings if not safety_mode else result.violations,
            )
            self._check_patterns(
                text,
                _TRAUMA_ATTACHMENT_PATTERNS,
                "Definitive trauma history or fixed attachment-style claim detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _ABUSE_ASSERTION_PATTERNS,
                "Definitive abuse, manipulation, or adjudicative labeling detected",
                result.violations,
            )
            if get_safety_policy().prohibit_mutualizing_serious_concerns:
                self._check_patterns(
                    text,
                    _MUTUALIZING_PATTERNS,
                    "Mutualizing or reconciliation pressure around serious concerns detected",
                    result.violations if safety_mode else result.warnings,
                )

        # Soft repair assist: lower confidence on risky findings (does not clear hard violations).
        self._downgrade_risky_findings(output, result)
        return result

    def validate_synthesis(
        self,
        report: SynthesisReport,
        *,
        safety_mode: bool = False,
    ) -> SafetyValidationResult:
        result = SafetyValidationResult()
        texts = [_strip_quoted_spans(t) for t in _collect_synthesis_texts(report)]

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
                result.warnings if not safety_mode else result.violations,
            )
            self._check_patterns(
                text,
                _TRAUMA_ATTACHMENT_PATTERNS,
                "Definitive trauma history or fixed attachment-style claim detected",
                result.violations,
            )
            self._check_patterns(
                text,
                _ABUSE_ASSERTION_PATTERNS,
                "Definitive abuse, manipulation, or adjudicative labeling detected",
                result.violations,
            )
            if get_safety_policy().prohibit_mutualizing_serious_concerns:
                self._check_patterns(
                    text,
                    _MUTUALIZING_PATTERNS,
                    "Mutualizing or reconciliation pressure around serious concerns detected",
                    result.violations if safety_mode else result.warnings,
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

    def _downgrade_risky_findings(
        self,
        output: ModuleRunOutput,
        result: SafetyValidationResult,
    ) -> None:
        """Force lower confidence on findings with adjudicative language (repair assist)."""
        risky = (
            _DIAGNOSIS_PATTERNS
            + _ABUSE_ASSERTION_PATTERNS
            + _TRAUMA_ATTACHMENT_PATTERNS
            + _MUTUALIZING_PATTERNS
        )
        for finding in output.findings:
            claim = _strip_quoted_spans(f"{finding.title} {finding.summary}")
            if not any(pattern.search(claim) for pattern in risky):
                continue
            if _CONFIDENCE_RANK.get(finding.confidence, 0) <= _CONFIDENCE_RANK[
                Confidence.EXPLORATORY
            ]:
                continue
            finding.confidence = Confidence.EXPLORATORY
            note = (
                "Confidence lowered: claim language was adjudicative or diagnostic; "
                "treat as exploratory only."
            )
            if note not in finding.limitations:
                finding.limitations.append(note)
            result.downgraded_finding_ids.append(finding.id)
            warning = (
                f"Finding {finding.id} confidence downgraded due to risky claim language"
            )
            if warning not in result.warnings:
                result.warnings.append(warning)


def _strip_quoted_spans(text: str) -> str:
    """Remove quoted spans so cited transcript text is not treated as model claims."""
    if not text:
        return ""
    return _QUOTE_SPAN.sub(" ", text)


def _collect_claim_texts(output: ModuleRunOutput) -> list[str]:
    texts = [output.executive_summary, output.raw_markdown_report]
    texts.extend(finding.title for finding in output.findings)
    texts.extend(finding.summary for finding in output.findings)
    texts.extend(output.recommendations)
    return [_strip_quoted_spans(text) for text in texts if text]


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
