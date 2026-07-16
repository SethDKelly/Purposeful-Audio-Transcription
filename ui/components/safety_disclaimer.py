import streamlit as st

from ui.components.constants import PRIVACY_NOTE, RETENTION_NOTE, SAFETY_DISCLAIMER


def render_safety_disclaimer() -> None:
    st.info(SAFETY_DISCLAIMER)


def render_safety_banner(*, safety_mode: bool = False, risk_level: str | None = None) -> None:
    if safety_mode:
        st.warning(
            "Safety-aware report mode is active. This run avoids reconciliation coaching "
            "and exploratory personality modules. Consider professional support for serious "
            "safety concerns."
        )
    elif risk_level in {"elevated", "high"}:
        st.warning(
            "This transcript may include elevated safety-related content. "
            "Analysis is evidence-limited and not a diagnosis or legal assessment. "
            "Consider professional support if you have safety concerns."
        )


def render_privacy_note() -> None:
    st.caption(PRIVACY_NOTE)
    st.caption(RETENTION_NOTE)
