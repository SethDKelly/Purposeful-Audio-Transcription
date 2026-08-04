"""Load and expose config-driven safety policy (phase 007)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from config.settings import settings

_DEFAULT_POLICY: dict[str, Any] = {
    "elevated_risk_triggers_safety_mode": True,
    "high_risk_triggers_safety_mode": True,
    "require_safety_framing": True,
    "prohibit_mutualizing_serious_concerns": True,
    "suppress_modules": [
        "exploratory_psychological_formulation",
        "narrative_identity_analysis",
    ],
    "modify_modules": [
        "trauma_informed_communication",
        "attachment_interaction_matrix",
    ],
}

_DEFAULT_SYNTHESIS_FRAMING = (
    "## Safety-aware framing\n\n"
    "This analysis may involve high-risk dynamics (threats, coercion, control, "
    "stalking, or self-harm cues). Stay evidence-limited and non-adjudicative.\n"
    "- Do not pressure reconciliation, mutual compromise, or shared-responsibility framing.\n"
    "- Do not coach both parties as equally accountable when control or threat cues dominate.\n"
    "- Do not mutualize serious safety concerns.\n"
    "- Recommend professional or emergency support where appropriate without diagnosing.\n"
    "- Avoid exploratory personality or identity interpretations; prioritize safety and boundaries."
)

_DEFAULT_MODULE_MODIFY_FRAMING = (
    "## Safety-aware module constraints\n\n"
    "Safety-aware mode is active for this run.\n"
    "- Stay non-diagnostic: do not assign disorders, personality labels, or trauma histories as fact.\n"
    "- Do not treat abuse, manipulation, or attachment style as settled determinations.\n"
    "- Prefer observed transcript cues with uncertainty and alternative explanations.\n"
    "- Do not mutualize serious safety concerns or push reconciliation."
)


class SafetyPolicy:
    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        payload = raw or {}
        policy = dict(_DEFAULT_POLICY)
        nested = payload.get("safety_policy")
        if isinstance(nested, dict):
            policy.update(nested)
        self._policy = policy
        self.synthesis_framing = str(
            payload.get("synthesis_framing") or _DEFAULT_SYNTHESIS_FRAMING
        ).strip()
        self.module_modify_framing = str(
            payload.get("module_modify_framing") or _DEFAULT_MODULE_MODIFY_FRAMING
        ).strip()

    @property
    def elevated_risk_triggers_safety_mode(self) -> bool:
        return bool(self._policy.get("elevated_risk_triggers_safety_mode", True))

    @property
    def high_risk_triggers_safety_mode(self) -> bool:
        return bool(self._policy.get("high_risk_triggers_safety_mode", True))

    @property
    def require_safety_framing(self) -> bool:
        return bool(self._policy.get("require_safety_framing", True))

    @property
    def prohibit_mutualizing_serious_concerns(self) -> bool:
        return bool(self._policy.get("prohibit_mutualizing_serious_concerns", True))

    @property
    def suppress_modules(self) -> frozenset[str]:
        items = self._policy.get("suppress_modules") or []
        return frozenset(str(item) for item in items)

    @property
    def modify_modules(self) -> frozenset[str]:
        items = self._policy.get("modify_modules") or []
        return frozenset(str(item) for item in items)

    def should_enable_safety_mode(self, risk_level: str) -> bool:
        level = (risk_level or "none").strip().lower()
        if level == "high":
            return self.high_risk_triggers_safety_mode
        if level == "elevated":
            return self.elevated_risk_triggers_safety_mode
        return False

    def should_suppress_module(self, module_id: str) -> bool:
        return module_id in self.suppress_modules

    def should_modify_module(self, module_id: str) -> bool:
        return module_id in self.modify_modules


def _policy_path() -> Path:
    configured = getattr(settings, "safety_policy_path", None)
    if configured:
        return Path(configured)
    return Path("./config/safety_policy.yaml")


@lru_cache(maxsize=1)
def load_safety_policy() -> SafetyPolicy:
    path = _policy_path()
    if not path.is_file():
        return SafetyPolicy()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return SafetyPolicy()
    return SafetyPolicy(raw)


def reload_safety_policy() -> SafetyPolicy:
    load_safety_policy.cache_clear()
    return load_safety_policy()


def get_safety_policy() -> SafetyPolicy:
    return load_safety_policy()
