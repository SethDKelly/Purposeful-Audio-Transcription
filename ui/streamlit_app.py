"""Streamlit UI for Purposeful Audio Transcription / RRE."""

import json

import httpx
import streamlit as st

from config.settings import settings
from ui.api_client import (
    API_BASE,
    create_transcript,
    fetch_health,
    fetch_modules,
    fetch_ollama_models,
    fetch_workflows,
    get_workflow_synthesis,
    module_display_name,
    module_name_map,
    run_workflow,
    transcribe_audio,
    update_transcript_speakers,
    upload_transcript_text,
)
from ui.components.evidence_quote_viewer import (
    build_quotes_index,
    index_modules_by_quote,
    render_evidence_quote_viewer,
)
from ui.components.exploration_panel import render_exploration_panel
from ui.components.module_tabs import render_module_tabs
from ui.components.report_exports import (
    build_coach_summary_markdown,
    build_mediation_brief_markdown,
    build_workflow_report_json,
    build_workflow_report_markdown,
    build_workflow_report_pdf,
)
from ui.components.safety_disclaimer import render_safety_disclaimer
from ui.components.synthesis_panel import render_synthesis_panel

ALLOWED_EXTENSIONS = sorted(settings.allowed_extensions)


def _status_indicator(ok: bool) -> str:
    return "Connected" if ok else "Unavailable"


@st.cache_data(ttl=30, show_spinner=False)
def _cached_health() -> dict | None:
    return fetch_health()


@st.cache_data(ttl=30, show_spinner=False)
def _cached_ollama_models() -> list[str]:
    return fetch_ollama_models()


@st.cache_data(ttl=30, show_spinner=False)
def _cached_workflows() -> list[dict]:
    return fetch_workflows()


@st.cache_data(ttl=30, show_spinner=False)
def _cached_modules() -> list[dict]:
    return fetch_modules()


def _apply_transcript_bundle(bundle: dict, *, source_name: str = "transcript") -> None:
    st.session_state.transcript = bundle["transcript"]["raw_text"]
    st.session_state.transcript_bundle = bundle
    st.session_state.transcript_meta = {
        "filename": source_name,
        "language": bundle["transcript"].get("language"),
        "transcript_id": bundle["transcript"]["id"],
        "speakers": bundle.get("speakers", []),
        "evidence_quotes": bundle.get("evidence_quotes", []),
    }
    st.session_state.workflow_run = None
    st.session_state.synthesis_report = None


def render_sidebar() -> None:
    st.sidebar.title("Status")
    health = _cached_health()
    if health is None:
        st.sidebar.error("API unreachable")
        st.sidebar.caption(f"Start the API at {API_BASE}")
        return

    st.sidebar.metric("API", health.get("status", "unknown").title())
    st.sidebar.markdown(
        f"- **ffmpeg:** {_status_indicator(health.get('ffmpeg_available', False))}"
    )
    st.sidebar.markdown(
        f"- **Ollama:** {_status_indicator(health.get('ollama_available', False))}"
    )
    st.sidebar.markdown(
        f"- **Whisper:** {_status_indicator(health.get('whisper_ready', False))}"
    )

    workflows = _cached_workflows()
    st.sidebar.divider()
    st.sidebar.markdown("**Workflows**")
    if workflows:
        for workflow in workflows:
            st.sidebar.caption(workflow["name"])
    else:
        st.sidebar.caption("No workflows configured")


def _render_workflow_progress(
    workflow_run: dict,
    module_names: dict[str, str],
) -> None:
    st.markdown("### Workflow progress")
    for module_run in workflow_run.get("module_runs", []):
        status = module_run.get("status", "unknown")
        module_id = module_run.get("module_id", "module")
        label = module_display_name(module_id, module_names)
        icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
        st.markdown(f"{icon} **{label}** — {status}")


def _render_report_dashboard(
    workflow_run: dict,
    synthesis: dict | None,
    quotes_by_id: dict[str, dict],
    speakers: list[dict],
    workflow_name: str,
    *,
    module_names: dict[str, str] | None = None,
    transcript_id: str | None = None,
    ollama_models: list[str] | None = None,
    default_model: str | None = None,
) -> None:
    render_safety_disclaimer()
    names = module_names or {}

    if workflow_run.get("status") != "completed":
        st.warning(
            f"Workflow status: {workflow_run.get('status')}. "
            f"{workflow_run.get('error_log') or ''}"
        )
        _render_workflow_progress(workflow_run, names)
        return

    _render_workflow_progress(workflow_run, names)

    overview_tab, modules_tab, evidence_tab, synthesis_tab, explore_tab = st.tabs(
        ["Overview", "Module reports", "Evidence map", "Synthesis", "Explore"]
    )

    with overview_tab:
        if synthesis:
            st.markdown(synthesis.get("executive_summary", ""))
            if synthesis.get("interventions"):
                st.markdown("#### Suggested next steps")
                for item in synthesis["interventions"][:3]:
                    st.markdown(f"- {item}")
        else:
            st.caption("Run a workflow with synthesis to see an integrated overview.")

    with modules_tab:
        render_module_tabs(workflow_run.get("module_runs", []), quotes_by_id)

    with evidence_tab:
        modules_using = index_modules_by_quote(workflow_run.get("module_runs", []))
        render_evidence_quote_viewer(
            quotes_by_id,
            modules_using=modules_using,
        )

    with synthesis_tab:
        if synthesis:
            render_synthesis_panel(synthesis, quotes_by_id)
        else:
            st.info("No synthesis report is available for this workflow.")

    with explore_tab:
        render_exploration_panel(
            workflow_run,
            transcript_id=transcript_id,
            quotes_by_id=quotes_by_id,
            ollama_models=ollama_models or [],
            default_model=default_model,
        )

    base_name = (
        st.session_state.transcript_meta.get("filename", "workflow_report")
        .rsplit(".", 1)[0]
    )
    redact_exports = st.checkbox(
        "Redact speaker labels and omit raw module reports from exports",
        value=False,
        key="export_redact",
    )
    export_md = build_workflow_report_markdown(
        workflow_run,
        synthesis,
        workflow_name=workflow_name,
        redact=redact_exports,
    )
    export_json = build_workflow_report_json(
        workflow_run,
        synthesis,
        transcript_meta=st.session_state.transcript_meta,
        redact=redact_exports,
    )
    export_pdf = build_workflow_report_pdf(
        workflow_run,
        synthesis,
        workflow_name=workflow_name,
        redact=redact_exports,
    )
    coach_summary = build_coach_summary_markdown(
        workflow_run,
        synthesis,
        workflow_name=workflow_name,
        redact=redact_exports,
    )
    show_mediation_brief = (
        workflow_run.get("workflow_id") == "mediation_brief"
        or any(
            module_run.get("module_id") == "mediation_analysis"
            for module_run in workflow_run.get("module_runs", [])
        )
    )
    mediation_brief = (
        build_mediation_brief_markdown(
            workflow_run,
            synthesis,
            workflow_name=workflow_name,
            redact=redact_exports,
        )
        if show_mediation_brief
        else None
    )

    col_md, col_json, col_pdf = st.columns(3)
    col_md.download_button(
        "Download workflow report (.md)",
        data=export_md,
        file_name=f"{base_name}_workflow_report.md",
        mime="text/markdown",
    )
    col_json.download_button(
        "Download workflow report (.json)",
        data=export_json,
        file_name=f"{base_name}_workflow_report.json",
        mime="application/json",
    )
    col_pdf.download_button(
        "Download workflow report (.pdf)",
        data=export_pdf,
        file_name=f"{base_name}_workflow_report.pdf",
        mime="application/pdf",
    )

    col_coach, col_mediation = st.columns(2)
    col_coach.download_button(
        "Download coach summary (.md)",
        data=coach_summary,
        file_name=f"{base_name}_coach_summary.md",
        mime="text/markdown",
    )
    if show_mediation_brief and mediation_brief:
        col_mediation.download_button(
            "Download mediation brief (.md)",
            data=mediation_brief,
            file_name=f"{base_name}_mediation_brief.md",
            mime="text/markdown",
        )


def main() -> None:
    st.set_page_config(
        page_title="Relationship Reasoning Engine",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Relationship Reasoning Engine")
    st.caption("Ingest transcripts, run structured workflows, explore evidence-linked reports.")

    render_sidebar()
    render_safety_disclaimer()

    workflows = _cached_workflows()
    ollama_models = _cached_ollama_models()
    module_names = module_name_map(_cached_modules())
    workflow_options = {workflow["name"]: workflow for workflow in workflows}

    for key, default in (
        ("transcript", ""),
        ("transcript_meta", {}),
        ("transcript_bundle", None),
        ("workflow_run", None),
        ("synthesis_report", None),
    ):
        if key not in st.session_state:
            st.session_state[key] = default

    # --- Step 1: Ingest ---
    st.subheader("Step 1 · Ingest")
    input_tab_audio, input_tab_text = st.tabs(["Audio", "Paste or upload text"])

    uploaded = None
    with input_tab_audio:
        uploaded = st.file_uploader(
            "Choose an audio file",
            type=[ext.lstrip(".") for ext in ALLOWED_EXTENSIONS],
            key="audio_uploader",
        )
        if uploaded is not None:
            st.audio(uploaded)
            st.caption(f"{uploaded.name} ({uploaded.size / (1024 * 1024):.2f} MB)")

    pasted_text = ""
    text_upload = None
    with input_tab_text:
        pasted_text = st.text_area(
            "Paste transcript",
            height=180,
            placeholder="Person A: Hello...\nPerson B: Hi...",
            key="pasted_transcript",
        )
        text_upload = st.file_uploader("Or upload a .txt transcript", type=["txt"], key="text_uploader")
        c1, c2 = st.columns(2)
        if c1.button("Prepare pasted transcript", disabled=not pasted_text.strip(), use_container_width=True):
            try:
                bundle = create_transcript(pasted_text.strip(), source_type="paste")
                _apply_transcript_bundle(bundle, source_name="pasted_transcript.txt")
                st.success("Transcript prepared.")
            except (RuntimeError, httpx.HTTPError) as exc:
                st.error(str(exc))
        if c2.button("Prepare uploaded transcript", disabled=text_upload is None, use_container_width=True):
            try:
                bundle = upload_transcript_text(text_upload.getvalue(), text_upload.name)
                _apply_transcript_bundle(bundle, source_name=text_upload.name)
                st.success("Transcript prepared.")
            except (RuntimeError, httpx.HTTPError) as exc:
                st.error(str(exc))

    if uploaded is not None and st.button("Transcribe audio", type="primary"):
        with st.status("Transcribing...", expanded=True) as status:
            try:
                result = transcribe_audio(uploaded.getvalue(), uploaded.name)
                bundle = create_transcript(
                    result.get("transcript", ""),
                    source_type="audio",
                    title=uploaded.name,
                    language=result.get("language"),
                )
                _apply_transcript_bundle(bundle, source_name=uploaded.name)
                st.session_state.transcript_meta.update(
                    {
                        "duration_seconds": result.get("duration_seconds"),
                        "segments": result.get("segments", []),
                    }
                )
                status.update(label="Transcription complete", state="complete")
            except (RuntimeError, httpx.HTTPError) as exc:
                status.update(label="Failed", state="error")
                st.error(str(exc))

    # --- Step 2: Prepare ---
    st.subheader("Step 2 · Prepare")
    if not st.session_state.transcript and not st.session_state.transcript_meta:
        st.info("Ingest a transcript to continue.")
    else:
        meta = st.session_state.transcript_meta
        cols = st.columns(3)
        if meta.get("language"):
            cols[0].metric("Language", meta["language"])
        if meta.get("transcript_id"):
            cols[1].metric("Transcript ID", meta["transcript_id"][:8] + "…")
        if meta.get("filename"):
            cols[2].metric("Source", meta["filename"])

        bundle = st.session_state.transcript_bundle
        if bundle and bundle.get("speakers"):
            with st.expander("Edit speaker display names", expanded=False):
                speaker_updates = []
                for speaker in bundle["speakers"]:
                    display_name = st.text_input(
                        f"Display name for {speaker['label']}",
                        value=speaker.get("display_name") or speaker["label"],
                        key=f"speaker_{speaker['id']}",
                    )
                    speaker_updates.append({"id": speaker["id"], "display_name": display_name})
                if st.button("Save speaker names"):
                    try:
                        updated = update_transcript_speakers(
                            bundle["transcript"]["id"],
                            speaker_updates,
                        )
                        st.session_state.transcript_bundle = updated
                        st.session_state.transcript_meta["speakers"] = updated["speakers"]
                        st.success("Speaker names updated.")
                    except (RuntimeError, httpx.HTTPError) as exc:
                        st.error(str(exc))

        st.session_state.transcript = st.text_area(
            "Transcript",
            value=st.session_state.transcript,
            height=220,
            label_visibility="collapsed",
        )

    # --- Step 3: Analyze ---
    st.subheader("Step 3 · Analyze")

    if not st.session_state.transcript:
        st.info("Prepare a transcript first.")
    elif not ollama_models:
        st.warning("No Ollama models available.")
    elif not workflows:
        st.warning("No workflows configured.")
    else:
        selected_workflow_name = st.selectbox(
            "Workflow",
            options=list(workflow_options.keys()),
        )
        workflow = workflow_options[selected_workflow_name]
        st.caption(workflow.get("description", ""))
        tone = workflow.get("output_tone")
        if tone:
            st.caption(f"Output tone: {tone.replace('_', ' ')}")
        recommended = workflow.get("recommended_model")
        if recommended:
            st.caption(f"Recommended model: {recommended}")
        st.caption(
            "Modules: "
            + ", ".join(
                module_display_name(module_id, module_names)
                for module_id in workflow.get("modules", [])
            )
            + f" · Est. {workflow.get('estimated_runtime', 'n/a')}"
        )

        default_model = settings.default_ollama_model or ollama_models[0]
        model_index = (
            ollama_models.index(default_model)
            if default_model in ollama_models
            else 0
        )
        selected_model = st.selectbox("Ollama model", options=ollama_models, index=model_index)

        transcript_id = st.session_state.transcript_meta.get("transcript_id")
        bundle_text = (st.session_state.transcript_bundle or {}).get("transcript", {}).get(
            "raw_text", ""
        )
        if transcript_id and bundle_text.strip() != st.session_state.transcript.strip():
            st.warning(
                "Transcript text was edited after preparation. Re-prepare to refresh "
                "evidence quotes, or run with the stored transcript ID."
            )

        if st.button("Run workflow", type="primary", disabled=not transcript_id):
            with st.status(f"Running {selected_workflow_name}...", expanded=True) as status:
                try:
                    for module_id in workflow.get("modules", []):
                        label = module_display_name(module_id, module_names)
                        st.write(f"Running {label}...")
                    result = run_workflow(
                        transcript_id=transcript_id,
                        workflow_id=workflow["id"],
                        model=selected_model,
                    )
                    st.session_state.workflow_run = result
                    st.session_state.synthesis_report = None
                    if result.get("status") == "completed":
                        try:
                            st.session_state.synthesis_report = get_workflow_synthesis(
                                result["id"]
                            )
                        except RuntimeError:
                            pass
                        status.update(label="Workflow complete", state="complete")
                    else:
                        status.update(label="Workflow failed", state="error")
                        st.error(result.get("error_log") or "Workflow failed.")
                except (RuntimeError, httpx.HTTPError) as exc:
                    status.update(label="Workflow failed", state="error")
                    st.error(str(exc))

    # --- Step 4: Report ---
    st.subheader("Step 4 · Report")
    workflow_run = st.session_state.workflow_run
    if workflow_run:
        quotes = st.session_state.transcript_meta.get("evidence_quotes", [])
        speakers = st.session_state.transcript_meta.get("speakers", [])
        quotes_by_id = build_quotes_index(quotes, speakers)
        workflow_name = next(
            (
                workflow["name"]
                for workflow in workflows
                if workflow["id"] == workflow_run.get("workflow_id")
            ),
            workflow_run.get("workflow_id", "Workflow"),
        )
        _render_report_dashboard(
            workflow_run,
            st.session_state.synthesis_report,
            quotes_by_id,
            speakers,
            workflow_name,
            module_names=module_names,
            transcript_id=st.session_state.transcript_meta.get("transcript_id"),
            ollama_models=ollama_models,
            default_model=settings.default_ollama_model or (ollama_models[0] if ollama_models else None),
        )
    else:
        st.info("Run a workflow to explore the evidence-linked report dashboard.")


if __name__ == "__main__":
    main()
