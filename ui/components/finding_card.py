import streamlit as st

from ui.components.confidence_badge import render_confidence_badge


def render_finding_card(
    finding: dict,
    *,
    module_id: str | None = None,
    quotes_by_id: dict[str, dict] | None = None,
    key_prefix: str = "finding",
) -> None:
    quotes_by_id = quotes_by_id or {}
    title = finding.get("title", "Finding")
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

        limitations = finding.get("limitations", [])
        if limitations:
            st.markdown("**Limitations**")
            for item in limitations:
                st.markdown(f"- {item}")


def _speaker_name(quote: dict) -> str:
    return quote.get("speaker_display_name") or quote.get("speaker_label") or "Speaker"
