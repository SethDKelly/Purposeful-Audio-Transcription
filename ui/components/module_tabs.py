import streamlit as st

from ui.components.executive_summary_panel import render_executive_summary_panel
from ui.components.finding_card import render_finding_card


def render_module_tabs(
    module_runs: list[dict],
    quotes_by_id: dict[str, dict],
    *,
    workflow_run_id: str | None = None,
    transcript_id: str | None = None,
) -> None:
    completed_runs = [
        run
        for run in module_runs
        if run.get("status") == "completed" and run.get("parsed_output")
    ]
    if not completed_runs:
        st.caption("No completed module outputs to display.")
        return

    tab_labels = [
        (run.get("parsed_output") or {}).get("module_id") or run.get("module_id", "Module")
        for run in completed_runs
    ]
    tabs = st.tabs(tab_labels)

    for tab, module_run in zip(tabs, completed_runs, strict=True):
        with tab:
            parsed = module_run.get("parsed_output") or {}
            module_id = parsed.get("module_id") or module_run.get("module_id")
            render_executive_summary_panel(
                parsed.get("executive_summary", ""),
                title=f"{module_id} summary",
            )

            findings = parsed.get("findings", [])
            if findings:
                st.markdown("### Findings")
                for index, finding in enumerate(findings):
                    render_finding_card(
                        finding,
                        module_id=module_id,
                        quotes_by_id=quotes_by_id,
                        key_prefix=f"{module_id}_{index}",
                        workflow_run_id=workflow_run_id,
                        transcript_id=transcript_id,
                    )

            recommendations = parsed.get("recommendations", [])
            if recommendations:
                st.markdown("### Recommendations")
                for item in recommendations:
                    st.markdown(f"- {item}")

            report = parsed.get("raw_markdown_report", "").strip()
            if report:
                with st.expander("Full module report"):
                    st.markdown(report)
