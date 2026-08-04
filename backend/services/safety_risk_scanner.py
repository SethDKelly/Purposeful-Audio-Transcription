"""Keyword/regex scan for high-risk transcript content (v1.0 P5 / phase 007)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

from backend.services.safety_policy import get_safety_policy


def _skip_in_safety_mode() -> frozenset[str]:
    return get_safety_policy().suppress_modules


# Backward-compatible alias used across engine/custom workflow imports.
SKIP_IN_SAFETY_MODE: frozenset[str] = frozenset(
    {
        "exploratory_psychological_formulation",
        "narrative_identity_analysis",
    }
)


def _refresh_skip_alias() -> None:
    """Keep module-level SKIP_IN_SAFETY_MODE aligned with loaded policy."""
    global SKIP_IN_SAFETY_MODE
    SKIP_IN_SAFETY_MODE = _skip_in_safety_mode()


_refresh_skip_alias()


def get_safety_synthesis_framing() -> str:
    return get_safety_policy().synthesis_framing


# Backward-compatible name used by prompt_compiler / tests.
SAFETY_SYNTHESIS_FRAMING = get_safety_synthesis_framing()


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

        policy = get_safety_policy()
        return SafetyScanResult(
            risk_level=highest,
            matched_categories=sorted(set(matched)),
            safety_mode_recommended=policy.should_enable_safety_mode(highest),
        )


safety_risk_scanner = SafetyRiskScanner()
