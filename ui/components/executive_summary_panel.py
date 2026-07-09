import streamlit as st


def render_executive_summary_panel(summary: str, *, title: str = "Executive summary") -> None:
    st.markdown(f"### {title}")
    if summary.strip():
        st.markdown(summary)
    else:
        st.caption("No executive summary available.")
