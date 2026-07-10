"""Shared API client helpers for the Streamlit UI."""

import httpx

from config.settings import settings

API_BASE = f"http://{settings.api_host}:{settings.api_port}"
# Whisper + CPU diarization on long audio can exceed 10 minutes on first model load.
TRANSCRIBE_TIMEOUT = 1800.0
PROCESS_TIMEOUT = 1200.0
WORKFLOW_TIMEOUT = 1800.0


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    raise RuntimeError(detail)


def fetch_health() -> dict | None:
    try:
        response = httpx.get(f"{API_BASE}/api/health", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except httpx.HTTPError:
        pass
    return None


def fetch_ollama_models() -> list[str]:
    try:
        response = httpx.get(f"{API_BASE}/api/models/ollama", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("models", [])
    except httpx.HTTPError:
        pass
    return []


def fetch_workflows() -> list[dict]:
    try:
        response = httpx.get(f"{API_BASE}/api/workflows", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("workflows", [])
    except httpx.HTTPError:
        pass
    return []


def fetch_modules() -> list[dict]:
    try:
        response = httpx.get(f"{API_BASE}/api/modules", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("modules", [])
    except httpx.HTTPError:
        pass
    return []


def module_name_map(modules: list[dict]) -> dict[str, str]:
    return {module["id"]: module["name"] for module in modules if module.get("id")}


def module_display_name(module_id: str, names: dict[str, str]) -> str:
    return names.get(module_id, module_id.replace("_", " ").title())


def transcribe_audio(
    file_bytes: bytes,
    filename: str,
    *,
    num_speakers: int | None = None,
) -> dict:
    data: dict[str, str] = {}
    if num_speakers is not None:
        data["num_speakers"] = str(num_speakers)

    response = httpx.post(
        f"{API_BASE}/api/transcribe",
        files={"file": (filename, file_bytes)},
        data=data,
        timeout=TRANSCRIBE_TIMEOUT,
    )
    _raise_for_status(response)
    return response.json()


def create_transcript(
    raw_text: str,
    source_type: str = "paste",
    title: str | None = None,
    language: str | None = None,
) -> dict:
    payload = {
        "raw_text": raw_text,
        "source_type": source_type,
        "title": title,
        "language": language,
    }
    response = httpx.post(f"{API_BASE}/api/transcripts", json=payload, timeout=30.0)
    _raise_for_status(response)
    return response.json()


def upload_transcript_text(file_bytes: bytes, filename: str, title: str | None = None) -> dict:
    response = httpx.post(
        f"{API_BASE}/api/transcripts/upload",
        files={"file": (filename, file_bytes)},
        data={"title": title or filename},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def update_transcript_speakers(transcript_id: str, speakers: list[dict]) -> dict:
    response = httpx.patch(
        f"{API_BASE}/api/transcripts/{transcript_id}/speakers",
        json={"speakers": speakers},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def process_audio(
    file_bytes: bytes,
    filename: str,
    workflow_id: str,
    model: str | None = None,
) -> dict:
    data: dict[str, str] = {"workflow_id": workflow_id}
    if model:
        data["model"] = model
    response = httpx.post(
        f"{API_BASE}/api/process",
        files={"file": (filename, file_bytes)},
        data=data,
        timeout=PROCESS_TIMEOUT,
    )
    _raise_for_status(response)
    return response.json()


def run_workflow(transcript_id: str, workflow_id: str, model: str | None = None) -> dict:
    payload = {"transcript_id": transcript_id, "model": model}
    response = httpx.post(
        f"{API_BASE}/api/workflows/{workflow_id}/run",
        json=payload,
        timeout=WORKFLOW_TIMEOUT,
    )
    _raise_for_status(response)
    return response.json()


def get_workflow_run(run_id: str) -> dict:
    response = httpx.get(f"{API_BASE}/api/workflow-runs/{run_id}", timeout=30.0)
    _raise_for_status(response)
    return response.json()


def get_workflow_synthesis(run_id: str) -> dict:
    response = httpx.get(f"{API_BASE}/api/workflow-runs/{run_id}/synthesis", timeout=30.0)
    _raise_for_status(response)
    return response.json()


def fetch_exploration_findings(run_id: str) -> list[dict]:
    response = httpx.get(
        f"{API_BASE}/api/workflow-runs/{run_id}/exploration/findings",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json().get("findings", [])


def fetch_finding_drilldown(run_id: str, finding_key: str) -> dict:
    response = httpx.get(
        f"{API_BASE}/api/workflow-runs/{run_id}/exploration/findings/{finding_key}",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_cross_module_alignment(run_id: str) -> dict:
    response = httpx.get(
        f"{API_BASE}/api/workflow-runs/{run_id}/exploration/cross-module",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_knowledge_graph(run_id: str) -> dict:
    response = httpx.get(
        f"{API_BASE}/api/workflow-runs/{run_id}/exploration/knowledge-graph",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_transcript_workflow_runs(transcript_id: str) -> list[dict]:
    response = httpx.get(
        f"{API_BASE}/api/transcripts/{transcript_id}/workflow-runs",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json().get("workflow_runs", [])


def compare_workflow_runs(workflow_run_ids: list[str]) -> dict:
    response = httpx.post(
        f"{API_BASE}/api/exploration/compare",
        json={"workflow_run_ids": workflow_run_ids},
        timeout=60.0,
    )
    _raise_for_status(response)
    return response.json()


def ask_workflow_followup(
    run_id: str,
    question: str,
    *,
    model: str | None = None,
    finding_key: str | None = None,
) -> dict:
    payload: dict[str, str] = {"question": question}
    if model:
        payload["model"] = model
    if finding_key:
        payload["finding_key"] = finding_key
    response = httpx.post(
        f"{API_BASE}/api/workflow-runs/{run_id}/exploration/ask",
        json=payload,
        timeout=120.0,
    )
    _raise_for_status(response)
    return response.json()
