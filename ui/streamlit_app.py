"""Streamlit UI for Purposeful Audio Transcription."""

import json
from collections.abc import Iterator

import httpx
import streamlit as st

from config.settings import settings

API_BASE = f"http://{settings.api_host}:{settings.api_port}"
ALLOWED_EXTENSIONS = sorted(settings.allowed_extensions)
TRANSCRIBE_TIMEOUT = 600.0
ANALYZE_TIMEOUT = 600.0
PROCESS_TIMEOUT = 1200.0


def _status_indicator(ok: bool) -> str:
    return "Connected" if ok else "Unavailable"


@st.cache_data(ttl=30, show_spinner=False)
def fetch_health() -> dict | None:
    try:
        response = httpx.get(f"{API_BASE}/api/health", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except httpx.HTTPError:
        pass
    return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_ollama_models() -> list[str]:
    try:
        response = httpx.get(f"{API_BASE}/api/models/ollama", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("models", [])
    except httpx.HTTPError:
        pass
    return []


@st.cache_data(ttl=30, show_spinner=False)
def fetch_purposes() -> list[dict]:
    try:
        response = httpx.get(f"{API_BASE}/api/purposes", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("purposes", [])
    except httpx.HTTPError:
        pass
    return []


def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    response = httpx.post(
        f"{API_BASE}/api/transcribe",
        files={"file": (filename, file_bytes)},
        timeout=TRANSCRIBE_TIMEOUT,
    )
    if response.status_code >= 400:
        detail = response.json().get("detail", response.text)
        raise RuntimeError(detail)
    return response.json()


def analyze_transcript(transcript: str, purpose_id: str, model: str | None) -> dict:
    payload = {
        "transcript": transcript,
        "purpose_id": purpose_id,
        "model": model,
    }
    response = httpx.post(
        f"{API_BASE}/api/analyze",
        json=payload,
        timeout=ANALYZE_TIMEOUT,
    )
    if response.status_code >= 400:
        detail = response.json().get("detail", response.text)
        raise RuntimeError(detail)
    return response.json()


def stream_analyze_transcript(
    transcript: str, purpose_id: str, model: str | None
) -> Iterator[str]:
    payload = {
        "transcript": transcript,
        "purpose_id": purpose_id,
        "model": model,
    }
    with httpx.stream(
        "POST",
        f"{API_BASE}/api/analyze/stream",
        json=payload,
        timeout=ANALYZE_TIMEOUT,
    ) as response:
        if response.status_code >= 400:
            error_body = response.read().decode("utf-8")
            try:
                detail = json.loads(error_body).get("detail", error_body)
            except json.JSONDecodeError:
                detail = error_body
            raise RuntimeError(detail)
        yield from response.iter_text()


def process_audio(
    file_bytes: bytes,
    filename: str,
    purpose_id: str,
    model: str | None,
) -> dict:
    response = httpx.post(
        f"{API_BASE}/api/process",
        files={"file": (filename, file_bytes)},
        data={"purpose_id": purpose_id, **({"model": model} if model else {})},
        timeout=PROCESS_TIMEOUT,
    )
    if response.status_code >= 400:
        detail = response.json().get("detail", response.text)
        raise RuntimeError(detail)
    return response.json()


def render_sidebar() -> None:
    st.sidebar.title("Status")

    health = fetch_health()
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

    if not health.get("ffmpeg_available"):
        st.sidebar.warning("Install ffmpeg for mp3/m4a support.")

    st.sidebar.divider()
    st.sidebar.markdown("**Whisper model**")
    st.sidebar.caption(settings.whisper_model)

    models = fetch_ollama_models()
    st.sidebar.markdown("**Ollama models**")
    if models:
        for model in models:
            st.sidebar.caption(model)
    else:
        st.sidebar.caption("No models pulled yet")

    purposes = fetch_purposes()
    st.sidebar.divider()
    st.sidebar.markdown("**Analysis purposes**")
    if purposes:
        for purpose in purposes:
            st.sidebar.caption(purpose["name"])
    else:
        st.sidebar.caption("No purposes configured")


def _default_model(
    purpose: dict | None,
    ollama_models: list[str],
) -> str | None:
    if purpose and purpose.get("default_model"):
        return purpose["default_model"]
    if settings.default_ollama_model:
        return settings.default_ollama_model
    return ollama_models[0] if ollama_models else None


def _render_analysis_exports(
    analysis: dict, base_name: str, *, show_content: bool = True
) -> None:
    if show_content:
        st.markdown("### Analysis result")
        st.caption(f"{analysis.get('purpose_name')} · {analysis.get('model')}")
        st.markdown(analysis.get("analysis", ""))

    export_md = (
        f"# {analysis.get('purpose_name')}\n\n"
        f"**Model:** {analysis.get('model')}\n\n"
        f"{analysis.get('analysis', '')}"
    )
    export_json = json.dumps(analysis, indent=2)

    col_md, col_json = st.columns(2)
    col_md.download_button(
        label="Download analysis (.md)",
        data=export_md,
        file_name=f"{base_name}_analysis.md",
        mime="text/markdown",
    )
    col_json.download_button(
        label="Download analysis (.json)",
        data=export_json,
        file_name=f"{base_name}_analysis.json",
        mime="application/json",
    )


def main() -> None:
    st.set_page_config(
        page_title="Purposeful Audio Transcription",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Purposeful Audio Transcription")
    st.caption("Upload local audio, transcribe with Whisper, analyze with Ollama.")

    render_sidebar()

    purposes = fetch_purposes()
    ollama_models = fetch_ollama_models()
    purpose_options = {purpose["name"]: purpose for purpose in purposes}

    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "transcript_meta" not in st.session_state:
        st.session_state.transcript_meta = {}
    if "analysis" not in st.session_state:
        st.session_state.analysis = None

    st.subheader("Step 1: Upload Audio")
    uploaded = st.file_uploader(
        "Choose an audio file",
        type=[ext.lstrip(".") for ext in ALLOWED_EXTENSIONS],
        help=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}",
    )

    if uploaded is not None:
        st.audio(uploaded)
        st.caption(f"{uploaded.name} ({uploaded.size / (1024 * 1024):.2f} MB)")

    one_shot_purpose = None
    one_shot_model = None
    if purposes and ollama_models:
        with st.expander("One-shot options", expanded=False):
            one_shot_purpose_name = st.selectbox(
                "Purpose for one-shot",
                options=list(purpose_options.keys()),
                key="one_shot_purpose",
            )
            one_shot_purpose = purpose_options[one_shot_purpose_name]
            one_shot_default = _default_model(one_shot_purpose, ollama_models)
            one_shot_model_index = (
                ollama_models.index(one_shot_default)
                if one_shot_default in ollama_models
                else 0
            )
            one_shot_model = st.selectbox(
                "Model for one-shot",
                options=ollama_models,
                index=one_shot_model_index,
                key="one_shot_model",
            )

    step1_cols = st.columns(2)
    transcribe_clicked = step1_cols[0].button(
        "Transcribe",
        type="primary",
        disabled=uploaded is None,
        use_container_width=True,
    )

    one_shot_disabled = (
        uploaded is None
        or not purposes
        or not ollama_models
    )
    one_shot_clicked = step1_cols[1].button(
        "Transcribe + Analyze",
        disabled=one_shot_disabled,
        use_container_width=True,
        help="Run transcription and analysis in one step",
    )

    if transcribe_clicked and uploaded is not None:
        with st.status("Transcribing audio...", expanded=True) as status:
            st.write("Uploading file to API...")
            try:
                result = transcribe_audio(uploaded.getvalue(), uploaded.name)
                st.session_state.transcript = result.get("transcript", "")
                st.session_state.transcript_meta = {
                    "language": result.get("language"),
                    "duration_seconds": result.get("duration_seconds"),
                    "segments": result.get("segments", []),
                    "filename": uploaded.name,
                }
                st.session_state.analysis = None
                status.update(label="Transcription complete", state="complete")
            except RuntimeError as exc:
                status.update(label="Transcription failed", state="error")
                st.error(str(exc))
            except httpx.HTTPError:
                status.update(label="Transcription failed", state="error")
                st.error(
                    f"Could not reach the API at {API_BASE}. "
                    "Run `scripts\\run_dev.ps1` or start uvicorn manually."
                )

    if one_shot_clicked and uploaded is not None and one_shot_purpose and one_shot_model:
        with st.status("Processing audio end-to-end...", expanded=True) as status:
            try:
                result = process_audio(
                    uploaded.getvalue(),
                    uploaded.name,
                    one_shot_purpose["id"],
                    one_shot_model,
                )
                st.session_state.transcript = result.get("transcript", "")
                st.session_state.transcript_meta = {
                    "language": result.get("language"),
                    "duration_seconds": result.get("duration_seconds"),
                    "segments": result.get("segments", []),
                    "filename": uploaded.name,
                }
                st.session_state.analysis = {
                    "purpose_id": result.get("purpose_id"),
                    "purpose_name": result.get("purpose_name"),
                    "model": result.get("model"),
                    "analysis": result.get("analysis", ""),
                }
                status.update(label="Processing complete", state="complete")
            except RuntimeError as exc:
                status.update(label="Processing failed", state="error")
                st.error(str(exc))
            except httpx.HTTPError:
                status.update(label="Processing failed", state="error")
                st.error(f"Could not reach the API at {API_BASE}.")

    st.subheader("Step 2: Transcript")

    if st.session_state.transcript or st.session_state.transcript_meta:
        meta = st.session_state.transcript_meta
        cols = st.columns(3)
        if meta.get("language"):
            cols[0].metric("Language", meta["language"])
        if meta.get("duration_seconds") is not None:
            cols[1].metric("Duration (s)", f"{meta['duration_seconds']:.1f}")
        if meta.get("filename"):
            cols[2].metric("Source", meta["filename"])

        st.caption("Edit the transcript before analysis if needed.")
        st.session_state.transcript = st.text_area(
            "Transcript",
            value=st.session_state.transcript,
            height=300,
            label_visibility="collapsed",
        )

        download_name = (
            meta.get("filename", "transcript").rsplit(".", 1)[0] + ".txt"
        )
        st.download_button(
            label="Download transcript",
            data=st.session_state.transcript,
            file_name=download_name,
            mime="text/plain",
        )

        segments = meta.get("segments", [])
        if segments:
            with st.expander("View segments with timestamps"):
                for segment in segments:
                    start = segment.get("start", 0)
                    end = segment.get("end", 0)
                    text = segment.get("text", "")
                    st.markdown(f"**[{start:.1f}s - {end:.1f}s]** {text}")
    else:
        st.info("Upload an audio file and click Transcribe to see results here.")

    st.subheader("Step 3: Analyze")

    if not st.session_state.transcript:
        st.info("Transcribe audio first, then run analysis here.")
    elif not purposes:
        st.warning("No analysis purposes are configured.")
    elif not ollama_models:
        st.warning(
            "No Ollama models available yet. Pull a model with "
            "`ollama pull <model>` or set `DEFAULT_OLLAMA_MODEL` in `.env` when ready."
        )
    else:
        selected_name = st.selectbox(
            "Analysis purpose",
            options=list(purpose_options.keys()),
        )
        selected_purpose = purpose_options[selected_name]
        st.caption(selected_purpose.get("description", ""))

        default_model = _default_model(selected_purpose, ollama_models)
        model_index = (
            ollama_models.index(default_model)
            if default_model in ollama_models
            else 0
        )
        selected_model = st.selectbox(
            "Ollama model",
            options=ollama_models,
            index=model_index,
        )

        use_streaming = st.checkbox(
            "Stream analysis output",
            value=True,
            help="Show tokens as they are generated",
        )

        analyze_clicked = st.button(
            "Analyze transcript",
            type="primary",
        )

        if analyze_clicked:
            transcript = st.session_state.transcript.strip()
            if not transcript:
                st.error("Transcript is empty.")
            else:
                try:
                    if use_streaming:
                        st.markdown("### Analysis result")
                        st.caption(f"{selected_name} · {selected_model}")
                        analysis_text = st.write_stream(
                            stream_analyze_transcript(
                                transcript,
                                selected_purpose["id"],
                                selected_model,
                            )
                        )
                        st.session_state.analysis = {
                            "purpose_id": selected_purpose["id"],
                            "purpose_name": selected_name,
                            "model": selected_model,
                            "analysis": analysis_text,
                        }
                    else:
                        with st.status("Analyzing transcript...", expanded=True) as status:
                            st.write(f"Running {selected_name} with {selected_model}...")
                            result = analyze_transcript(
                                transcript,
                                selected_purpose["id"],
                                selected_model,
                            )
                            st.session_state.analysis = result
                            status.update(label="Analysis complete", state="complete")
                except RuntimeError as exc:
                    st.error(str(exc))
                except httpx.HTTPError:
                    st.error(f"Could not reach the API at {API_BASE}.")

        if st.session_state.analysis:
            base_name = (
                st.session_state.transcript_meta.get("filename", "analysis")
                .rsplit(".", 1)[0]
            )
            streamed_this_run = analyze_clicked and use_streaming
            _render_analysis_exports(
                st.session_state.analysis,
                base_name,
                show_content=not streamed_this_run,
            )


if __name__ == "__main__":
    main()
