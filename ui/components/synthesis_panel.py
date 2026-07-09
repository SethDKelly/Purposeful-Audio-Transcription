import streamlit as st

from ui.components.executive_summary_panel import render_executive_summary_panel
from ui.components.finding_card import render_finding_card


def render_synthesis_panel(
    synthesis: dict,
    quotes_by_id: dict[str, dict],
) -> None:
    render_executive_summary_panel(
        synthesis.get("executive_summary", ""),
        title="Integrated executive summary",
    )

    convergence = synthesis.get("convergence", [])
    if convergence:
        st.markdown("### Convergence")
        for item in convergence:
            st.markdown(f"- {item}")

    divergence = synthesis.get("divergence", [])
    if divergence:
        st.markdown("### Divergence")
        for item in divergence:
            st.markdown(f"- {item}")

    integrated_model = synthesis.get("integrated_model", [])
    if integrated_model:
        st.markdown("### Integrated model")
        for item in integrated_model:
            st.markdown(f"- {item}")

    _render_finding_group(
        "Strongest findings",
        synthesis.get("high_confidence_findings", []),
        quotes_by_id,
        prefix="high",
    )
    _render_finding_group(
        "Moderate-confidence findings",
        synthesis.get("moderate_confidence_findings", []),
        quotes_by_id,
        prefix="moderate",
    )
    _render_finding_group(
        "Exploratory hypotheses",
        synthesis.get("exploratory_hypotheses", []),
        quotes_by_id,
        prefix="exploratory",
    )

    interventions = synthesis.get("interventions", [])
    if interventions:
        st.markdown("### Highest-leverage improvements")
        for item in interventions:
            st.markdown(f"- {item}")

    questions = synthesis.get("outstanding_questions", [])
    if questions:
        with st.expander("Outstanding questions"):
            for item in questions:
                st.markdown(f"- {item}")

    limitations = synthesis.get("limitations", [])
    if limitations:
        with st.expander("Limitations"):
            for item in limitations:
                st.markdown(f"- {item}")

    safety_flags = synthesis.get("safety_flags", [])
    if safety_flags:
        with st.expander("Safety flags"):
            for item in safety_flags:
                st.markdown(f"- {item}")


def _render_finding_group(
    title: str,
    findings: list[dict],
    quotes_by_id: dict[str, dict],
    *,
    prefix: str,
) -> None:
    if not findings:
        return
    with st.expander(f"{title} ({len(findings)})", expanded=title.startswith("Strongest")):
        for index, finding in enumerate(findings):
            render_finding_card(
                finding,
                quotes_by_id=quotes_by_id,
                key_prefix=f"{prefix}_{index}",
            )
