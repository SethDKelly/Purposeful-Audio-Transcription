import streamlit as st

from ui.api_client import submit_finding_feedback
from ui.components.confidence_badge import render_confidence_badge


def render_finding_card(
    finding: dict,
    *,
    module_id: str | None = None,
    quotes_by_id: dict[str, dict] | None = None,
    key_prefix: str = "finding",
    workflow_run_id: str | None = None,
    transcript_id: str | None = None,
) -> None:
    quotes_by_id = quotes_by_id or {}
    title = finding.get("title", "Finding")
    finding_id = finding.get("id") or title
    finding_key = f"{module_id}:{finding_id}" if module_id else str(finding_id)
    with st.container(border=True):
        st.markdown(f"#### {title}")
        if module_id:
            st.caption(f"Source module: {module_id}")
        render_confidence_badge(str(finding.get("confidence", "moderate")))
        summary = finding.get("summary", "")
        if summary:
            st.markdown(summary)

        quote_ids = finding.get("evidence_quote_ids", [])
        if quote_ids:
            st.markdown("**Evidence**")
            for quote_id in quote_ids:
                quote = quotes_by_id.get(quote_id)
                if quote:
                    speaker_name = _speaker_name(quote)
                    st.markdown(
                        f"- **{quote_id}** ({speaker_name}): {quote.get('text', '')}"
                    )
                else:
                    st.markdown(f"- **{quote_id}**")

        alternatives = finding.get("alternative_explanations", [])
        if alternatives:
            st.markdown("**Alternative explanations**")
            for item in alternatives:
                st.markdown(f"- {item}")

        if workflow_run_id:
            with st.expander("Analyst feedback", expanded=False):
                rating = st.radio(
                    "Was this finding helpful?",
                    options=["helpful", "unhelpful", "unsure"],
                    horizontal=True,
                    key=f"{key_prefix}_{finding_key}_rating",
                )
                note = st.text_input(
                    "Optional note",
                    key=f"{key_prefix}_{finding_key}_note",
                )
                if st.button("Save feedback", key=f"{key_prefix}_{finding_key}_save"):
                    try:
                        submit_finding_feedback(
                            workflow_run_id,
                            finding_key,
                            rating=rating,
                            note=note.strip() or None,
                            transcript_id=transcript_id,
                        )
                        st.success("Feedback saved.")
                    except RuntimeError as exc:
                        st.error(str(exc))

        limitations = finding.get("limitations", [])
        if limitations:
            st.markdown("**Limitations**")
            for item in limitations:
                st.markdown(f"- {item}")


def _speaker_name(quote: dict) -> str:
    return quote.get("speaker_display_name") or quote.get("speaker_label") or "Speaker"
