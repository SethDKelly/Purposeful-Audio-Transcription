"""Keyword/regex scan for high-risk transcript content (v1.0 P5)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

# Exploratory modules skipped when safety_mode is active.
SKIP_IN_SAFETY_MODE: frozenset[str] = frozenset(
    {
        "exploratory_psychological_formulation",
        "narrative_identity_analysis",
    }
)

SAFETY_SYNTHESIS_FRAMING = (
    "## Safety-aware framing\n\n"
    "This analysis may involve high-risk dynamics (threats, coercion, control, "
    "stalking, or self-harm cues). Stay evidence-limited and non-adjudicative.\n"
    "- Do not pressure reconciliation, mutual compromise, or shared-responsibility framing.\n"
    "- Do not coach both parties as equally accountable when control or threat cues dominate.\n"
    "- Recommend professional or emergency support where appropriate without diagnosing.\n"
    "- Avoid exploratory personality or identity interpretations; prioritize safety and boundaries."
)


class SafetyScanResult(BaseModel):
    risk_level: str  # none | elevated | high
    matched_categories: list[str] = Field(default_factory=list)
    safety_mode_recommended: bool = False


@dataclass(frozen=True)
class _RiskPattern:
    category: str
    level: str  # elevated | high
    patterns: tuple[re.Pattern[str], ...]


def _compile(patterns: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(p, re.IGNORECASE) for p in patterns)


_RISK_PATTERNS: tuple[_RiskPattern, ...] = (
    _RiskPattern(
        "self_harm",
        "high",
        _compile(
            (
                r"\b(kill myself|end my life|suicide|suicidal|self[- ]harm|cut myself)\b",
                r"\b(want to die|don't want to live|better off dead)\b",
            )
        ),
    ),
    _RiskPattern(
        "threats",
        "high",
        _compile(
            (
                r"\b(i will kill you|i'll kill you|going to kill you)\b",
                r"\b(hurt you|make you pay|you'll regret|destroy you)\b",
            )
        ),
    ),
    _RiskPattern(
        "coercion",
        "elevated",
        _compile(
            (
                r"\b(do what i say or else|you have no choice|i won't let you leave)\b",
                r"\b(if you leave|if you tell anyone)\b.*\b(i will|i'll|you'll)\b",
            )
        ),
    ),
    _RiskPattern(
        "stalking",
        "elevated",
        _compile(
            (
                r"\b(following you|watching you|tracking you|know where you are)\b",
                r"\b(showed up at (your|my) (work|home|house))\b",
            )
        ),
    ),
    _RiskPattern(
        "severe_control",
        "elevated",
        _compile(
            (
                r"\b(control (every|all) (aspect|part|detail))\b",
                r"\b(not allowed to (see|talk|leave|work|friends))\b",
                r"\b(take away your (phone|keys|money|passport))\b",
            )
        ),
    ),
)


class SafetyRiskScanner:
    def scan(self, text: str) -> SafetyScanResult:
        normalized = (text or "").strip()
        if not normalized:
            return SafetyScanResult(risk_level="none")

        matched: list[str] = []
        highest = "none"
        for group in _RISK_PATTERNS:
            if any(pattern.search(normalized) for pattern in group.patterns):
                matched.append(group.category)
                if group.level == "high":
                    highest = "high"
                elif highest != "high" and group.level == "elevated":
                    highest = "elevated"

        return SafetyScanResult(
            risk_level=highest,
            matched_categories=sorted(set(matched)),
            safety_mode_recommended=highest == "high",
        )


safety_risk_scanner = SafetyRiskScanner()
