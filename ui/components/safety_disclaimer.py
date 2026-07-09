import streamlit as st

from ui.components.constants import SAFETY_DISCLAIMER


def render_safety_disclaimer() -> None:
    st.info(SAFETY_DISCLAIMER)
