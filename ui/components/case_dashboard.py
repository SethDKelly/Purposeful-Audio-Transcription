"""Case dashboard UI (v0.9 P2)."""

from __future__ import annotations

import streamlit as st

from ui.api_client import (
    assign_transcript_case,
    compare_case_transcripts,
    create_case,
    get_case,
    list_cases,
)


def render_case_dashboard(current_transcript_id: str | None = None) -> None:
    st.subheader("Cases")
    st.caption("Group transcripts over time for longitudinal comparison.")

    try:
        cases = list_cases()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    create_col, assign_col = st.columns(2)
    with create_col:
        with st.form("create_case_form", clear_on_submit=True):
            title = st.text_input("New case title", placeholder="Couple / family label")
            notes = st.text_area("Notes", height=80)
            if st.form_submit_button("Create case", use_container_width=True):
                if not title.strip():
                    st.warning("Title is required.")
                else:
                    try:
                        created = create_case(title.strip(), notes=notes.strip() or None)
                        st.success(f"Created case: {created['title']}")
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

    with assign_col:
        if current_transcript_id:
            case_labels = {c["id"]: c["title"] for c in cases}
            options = ["(none)"] + list(case_labels.keys())
            selected = st.selectbox(
                "Assign current transcript",
                options=options,
                format_func=lambda value: "(none)" if value == "(none)" else case_labels[value],
                key="assign_case_select",
            )
            session_label = st.text_input("Session label", placeholder="Session 2", key="session_label")
            if st.button("Save assignment", use_container_width=True):
                try:
                    assign_transcript_case(
                        current_transcript_id,
                        case_id=None if selected == "(none)" else selected,
                        session_label=session_label.strip() or None,
                    )
                    st.success("Transcript assignment updated.")
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))
        else:
            st.info("Prepare a transcript to assign it to a case.")

    if not cases:
        st.caption("No cases yet.")
        return

    selected_case_id = st.selectbox(
        "Open case",
        options=[c["id"] for c in cases],
        format_func=lambda cid: next(c["title"] for c in cases if c["id"] == cid),
        key="case_dashboard_select",
    )
    try:
        detail = get_case(selected_case_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    case = detail["case"]
    transcripts = detail.get("transcripts", [])
    st.markdown(f"**{case['title']}**")
    if case.get("notes"):
        st.caption(case["notes"])

    rows = [
        {
            "session": t.get("session_label") or t.get("title"),
            "title": t.get("title"),
            "ready": t.get("analysis_ready"),
            "workflow_runs": t.get("workflow_run_count", 0),
            "created": t.get("created_at"),
        }
        for t in transcripts
    ]
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No transcripts linked to this case yet.")

    if len(transcripts) >= 2 and st.button("Compare sessions in this case"):
        try:
            comparison = compare_case_transcripts(selected_case_id)
            st.session_state["case_comparison"] = comparison
        except RuntimeError as exc:
            st.error(str(exc))

    comparison = st.session_state.get("case_comparison")
    if comparison and comparison.get("case_id") == selected_case_id:
        st.markdown("#### Longitudinal comparison")
        counts = comparison.get("counts", {})
        st.caption(
            f"{counts.get('transcripts', 0)} transcripts · "
            f"{counts.get('shared_themes', 0)} shared themes · "
            f"{counts.get('new_themes', 0)} newer-only · "
            f"{counts.get('resolved_themes', 0)} earlier-only"
        )
        if comparison.get("shared_themes"):
            st.markdown("**Shared themes**")
            st.dataframe(comparison["shared_themes"], use_container_width=True, hide_index=True)
        if comparison.get("new_themes"):
            st.markdown("**Appeared in later sessions**")
            st.dataframe(comparison["new_themes"], use_container_width=True, hide_index=True)
        if comparison.get("resolved_themes"):
            st.markdown("**Present earlier, not later**")
            st.dataframe(comparison["resolved_themes"], use_container_width=True, hide_index=True)
        if comparison.get("recurring_evidence_quote_ids"):
            st.caption(
                "Recurring evidence quote IDs: "
                + ", ".join(comparison["recurring_evidence_quote_ids"][:20])
            )
