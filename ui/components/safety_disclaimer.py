import streamlit as st

from ui.components.constants import PRIVACY_NOTE, SAFETY_DISCLAIMER


def render_safety_disclaimer() -> None:
    st.info(SAFETY_DISCLAIMER)


def render_privacy_note() -> None:
    st.caption(PRIVACY_NOTE)
