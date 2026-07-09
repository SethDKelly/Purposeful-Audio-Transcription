import streamlit as st

from ui.components.constants import CONFIDENCE_LABELS


def confidence_label(confidence: str) -> str:
    return CONFIDENCE_LABELS.get(confidence, confidence.replace("_", " ").title())


def render_confidence_badge(confidence: str) -> None:
    st.markdown(f"**Confidence:** {confidence_label(confidence)}")
