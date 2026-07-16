import streamlit as st

from ui.api_client import (
    ask_workflow_followup,
    compare_workflow_runs,
    fetch_cross_module_alignment,
    fetch_exploration_findings,
    fetch_finding_drilldown,
    fetch_knowledge_graph,
    fetch_structured_graph,
    fetch_transcript_workflow_runs,
)


def render_exploration_panel(
    workflow_run: dict,
    *,
    transcript_id: str | None,
    quotes_by_id: dict[str, dict],
    llm_models: list[str],
    default_model: str | None = None,
) -> None:
    run_id = workflow_run.get("id")
    if not run_id:
        st.caption("No workflow run selected.")
        return

    if workflow_run.get("status") != "completed":
        st.info("Complete the workflow to use interactive exploration.")
        return

    (
        inventory_tab,
        drilldown_tab,
        cross_module_tab,
        compare_tab,
        graph_tab,
        ask_tab,
    ) = st.tabs(
        [
            "Structured inventory",
            "Why this finding?",
            "Cross-module",
            "Compare sessions",
            "Knowledge graph",
            "Ask a question",
        ]
    )

    with inventory_tab:
        _render_structured_inventory(run_id)

    with drilldown_tab:
        _render_finding_drilldown(run_id, quotes_by_id)

    with cross_module_tab:
        _render_cross_module(run_id)

    with compare_tab:
        _render_compare_sessions(transcript_id, workflow_run)

    with graph_tab:
        _render_knowledge_graph(run_id)

    with ask_tab:
        _render_ask_question(run_id, llm_models, default_model)


def _render_structured_inventory(run_id: str) -> None:
    try:
        inventory = fetch_structured_graph(run_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    counts = inventory.get("counts", {})
    st.caption(
        f"{counts.get('findings', 0)} findings · "
        f"{counts.get('constructs', 0)} constructs · "
        f"{counts.get('relationships', 0)} relationships"
    )

    findings = inventory.get("findings", [])
    constructs = inventory.get("constructs", [])
    relationships = inventory.get("relationships", [])

    type_filter = st.multiselect(
        "Filter constructs by ontology type",
        options=sorted({c.get("ontology_type", "") for c in constructs if c.get("ontology_type")}),
    )
    confidence_filter = st.multiselect(
        "Filter by confidence",
        options=sorted(
            {
                *(f.get("confidence") for f in findings if f.get("confidence")),
                *(c.get("confidence") for c in constructs if c.get("confidence")),
            }
        ),
    )
    module_filter = st.multiselect(
        "Filter by module",
        options=sorted(
            {
                *(f.get("module_id") for f in findings if f.get("module_id")),
                *(c.get("module_id") for c in constructs if c.get("module_id")),
            }
        ),
    )

    def _pass_filters(row: dict, *, type_key: str | None = None) -> bool:
        if type_filter and type_key and row.get(type_key) not in type_filter:
            return False
        if confidence_filter and row.get("confidence") not in confidence_filter:
            return False
        if module_filter and row.get("module_id") not in module_filter:
            return False
        return True

    st.subheader("Constructs")
    construct_rows = [
        {
            "label": c.get("label"),
            "type": c.get("ontology_type"),
            "confidence": c.get("confidence"),
            "convergence": c.get("convergence_score"),
            "module": c.get("module_id"),
            "quotes": ", ".join(c.get("evidence_quote_ids") or []),
            "sources": len(c.get("sources") or []),
        }
        for c in constructs
        if _pass_filters(c, type_key="ontology_type")
    ]
    if construct_rows:
        st.dataframe(construct_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No constructs match the current filters.")

    st.subheader("Relationships")
    relationship_rows = [
        {
            "source": r.get("source_construct_id"),
            "type": r.get("relationship_type"),
            "target": r.get("target_construct_id"),
            "confidence": r.get("confidence"),
            "module": r.get("module_id"),
            "warning": r.get("link_warning") or r.get("ontology_warning") or "",
        }
        for r in relationships
        if _pass_filters(r)
    ]
    if relationship_rows:
        st.dataframe(relationship_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No relationships match the current filters.")

    st.subheader("Findings")
    finding_rows = [
        {
            "title": f.get("title"),
            "type": f.get("type"),
            "confidence": f.get("confidence"),
            "module": f.get("module_id"),
            "quotes": ", ".join(f.get("evidence_quote_ids") or []),
        }
        for f in findings
        if _pass_filters(f)
    ]
    if finding_rows:
        st.dataframe(finding_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No findings match the current filters.")


def _render_finding_drilldown(run_id: str, quotes_by_id: dict[str, dict]) -> None:
    try:
        findings = fetch_exploration_findings(run_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not findings:
        st.caption("No indexed findings available.")
        return

    labels = {
        item["finding_key"]: f"{item['module_id']} · {item.get('title', item['finding_key'])}"
        for item in findings
    }
    selected_key = st.selectbox(
        "Select a finding",
        options=list(labels.keys()),
        format_func=lambda key: labels[key],
        key="explore_finding_selector",
    )

    try:
        drilldown = fetch_finding_drilldown(run_id, selected_key)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    finding = drilldown.get("finding", {})
    st.markdown(f"### {finding.get('title', 'Finding')}")
    st.caption(
        f"Module: {drilldown.get('module_id')} · Confidence: {finding.get('confidence', 'n/a')}"
    )
    if finding.get("summary"):
        st.markdown(finding["summary"])

    st.markdown("#### Evidence chain")
    for quote in drilldown.get("evidence_chain", []):
        with st.container(border=True):
            st.markdown(f"**{quote['quote_id']}** · Turn {quote['turn_index']} · {quote['speaker']}")
            st.markdown(f"> {quote['text']}")
            if quote.get("context_before"):
                st.caption(f"Before: {quote['context_before']}")
            if quote.get("context_after"):
                st.caption(f"After: {quote['context_after']}")

    related = drilldown.get("related_findings", [])
    if related:
        st.markdown("#### Related findings in other modules")
        for item in related:
            st.markdown(
                f"- **{item['module_id']}** — {item.get('title')} "
                f"(shared quotes: {', '.join(item.get('shared_evidence_quote_ids', []))})"
            )

    constructs = drilldown.get("linked_constructs", [])
    if constructs:
        st.markdown("#### Linked constructs")
        for construct in constructs:
            st.markdown(f"- **{construct.get('label')}** ({construct.get('type', 'construct')})")


def _render_cross_module(run_id: str) -> None:
    try:
        alignment = fetch_cross_module_alignment(run_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    synthesis = alignment.get("synthesis")
    if synthesis:
        if synthesis.get("convergence"):
            st.markdown("#### Synthesis convergence")
            for item in synthesis["convergence"]:
                st.markdown(f"- {item}")
        if synthesis.get("divergence"):
            st.markdown("#### Synthesis divergence")
            for item in synthesis["divergence"]:
                st.markdown(f"- {item}")

    agreements = alignment.get("agreements", [])
    if agreements:
        st.markdown("#### Module agreements")
        for group in agreements:
            modules = " ↔ ".join(group.get("modules", []))
            quotes = ", ".join(group.get("shared_evidence_quote_ids", []))
            st.markdown(f"- **{modules}** — shared evidence: {quotes or 'title overlap'}")
    else:
        st.caption("No cross-module agreement groups detected.")

    disagreements = alignment.get("disagreements", [])
    if disagreements:
        st.markdown("#### Module tensions")
        for group in disagreements:
            modules = " ↔ ".join(group.get("modules", []))
            st.markdown(f"- **{modules}** — shared evidence with differing emphasis")
            for note in group.get("notes", []):
                st.caption(note)


def _render_compare_sessions(transcript_id: str | None, current_run: dict) -> None:
    if not transcript_id:
        st.caption("Transcript ID unavailable for session comparison.")
        return

    try:
        runs = fetch_transcript_workflow_runs(transcript_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if len(runs) < 2:
        st.info("Run this workflow at least twice on the same transcript to compare sessions.")
        return

    options = {
        run["id"]: f"{run['workflow_id']} · {run['completed_at'] or run['started_at']}"
        for run in runs
    }
    selected_ids = st.multiselect(
        "Select workflow runs to compare",
        options=list(options.keys()),
        default=[current_run["id"]] if current_run.get("id") in options else [],
        format_func=lambda run_id: options[run_id],
        key="compare_run_selector",
    )

    if len(selected_ids) < 2:
        st.caption("Select at least two completed runs.")
        return

    if st.button("Compare selected runs", key="compare_runs_button"):
        try:
            comparison = compare_workflow_runs(selected_ids)
        except RuntimeError as exc:
            st.error(str(exc))
            return

        st.markdown("#### Shared themes")
        themes = comparison.get("shared_themes", [])
        if themes:
            for theme in themes[:10]:
                st.markdown(
                    f"- **{theme['theme']}** across {len(theme['workflow_run_ids'])} runs"
                )
        else:
            st.caption("No shared themes detected.")

        recurring = comparison.get("recurring_evidence_quote_ids", [])
        if recurring:
            st.markdown("#### Recurring evidence quotes")
            for item in recurring[:10]:
                st.markdown(
                    f"- **{item['quote_id']}** in {len(item['workflow_run_ids'])} runs"
                )


def _render_knowledge_graph(run_id: str) -> None:
    try:
        graph = fetch_knowledge_graph(run_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not nodes:
        st.info("No constructs were returned by modules for this run.")
        return

    st.markdown("#### Constructs")
    for node in nodes:
        quotes = ", ".join(node.get("evidence_quote_ids", []))
        st.markdown(
            f"- **{node['label']}** ({node['type']}) · module {node['module_id']}"
            + (f" · evidence: {quotes}" if quotes else "")
        )

    if edges:
        st.markdown("#### Relationships")
        mermaid_lines = ["graph LR"]
        for edge in edges:
            label = edge.get("relationship_type", "related").replace(" ", "_")
            mermaid_lines.append(
                f'  {edge["source"].replace(":", "_")}["{edge["source"].split(":", 1)[-1]}"]'
                f' -->|{label}| '
                f'{edge["target"].replace(":", "_")}["{edge["target"].split(":", 1)[-1]}"]'
            )
        st.markdown("```mermaid\n" + "\n".join(mermaid_lines) + "\n```")


def _render_ask_question(
    run_id: str,
    llm_models: list[str],
    default_model: str | None,
) -> None:
    if not llm_models:
        st.warning("No LLM models available.")
        return

    try:
        findings = fetch_exploration_findings(run_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    scope_options = {"": "Entire workflow run"}
    for item in findings:
        scope_options[item["finding_key"]] = (
            f"{item['module_id']} · {item.get('title', item['finding_key'])}"
        )

    finding_key = st.selectbox(
        "Scope (optional)",
        options=list(scope_options.keys()),
        format_func=lambda key: scope_options[key],
        key="ask_scope_selector",
    )
    model_index = (
        llm_models.index(default_model) if default_model in llm_models else 0
    )
    selected_model = st.selectbox(
        "LLM model",
        options=llm_models,
        index=model_index,
        key="ask_model_selector",
    )
    question = st.text_area(
        "Ask about stored findings",
        placeholder="Why did the system conclude there was a repair attempt?",
        key="ask_question_input",
    )

    if st.button("Ask", type="primary", disabled=not question.strip(), key="ask_button"):
        try:
            response = ask_workflow_followup(
                run_id,
                question.strip(),
                model=selected_model,
                finding_key=finding_key or None,
            )
        except RuntimeError as exc:
            st.error(str(exc))
            return

        st.markdown("#### Answer")
        st.markdown(response.get("answer", ""))
        scope = response.get("context_scope")
        if scope:
            st.caption(f"Context scope: {scope}")
