"""Shared API client helpers for the Streamlit UI."""

import httpx

from config.settings import settings

API_BASE = settings.api_base_url
# Amazon Transcribe jobs can take several minutes on longer audio.
# Keep above backend TRANSCRIBE_TIMEOUT_SECONDS (default 3600).
TRANSCRIBE_TIMEOUT = 3900.0
PROCESS_TIMEOUT = 1200.0
WORKFLOW_TIMEOUT = 3600.0


def _api_headers() -> dict[str, str]:
    """Attach API key when configured (V07-1b)."""
    if settings.api_key:
        return {"X-API-Key": settings.api_key}
    return {}


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    request_id = response.headers.get("X-Request-ID")
    detail: object
    try:
        body = response.json()
        detail = body.get("detail", response.text)
        if not request_id:
            request_id = body.get("request_id")
    except Exception:
        detail = response.text
    message = str(detail)
    if request_id:
        message = f"{message} (request ID: {request_id})"
    raise RuntimeError(message)


def _get(path: str, *, timeout: float) -> httpx.Response:
    return httpx.get(
        f"{API_BASE}{path}",
        headers=_api_headers(),
        timeout=timeout,
    )


def _post(
    path: str,
    *,
    timeout: float,
    json: dict | None = None,
    files=None,
    data: dict | None = None,
) -> httpx.Response:
    return httpx.post(
        f"{API_BASE}{path}",
        headers=_api_headers(),
        timeout=timeout,
        json=json,
        files=files,
        data=data,
    )


def _patch(path: str, *, timeout: float, json: dict) -> httpx.Response:
    return httpx.patch(
        f"{API_BASE}{path}",
        headers=_api_headers(),
        timeout=timeout,
        json=json,
    )


def _delete(path: str, *, timeout: float) -> httpx.Response:
    return httpx.delete(
        f"{API_BASE}{path}",
        headers=_api_headers(),
        timeout=timeout,
    )


def fetch_health() -> dict | None:
    try:
        response = _get("/api/health", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except httpx.HTTPError:
        pass
    return None


def fetch_llm_models() -> list[str]:
    try:
        response = _get("/api/models", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("models", [])
    except httpx.HTTPError:
        pass
    return []


def fetch_workflows() -> list[dict]:
    try:
        response = _get("/api/workflows", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("workflows", [])
    except httpx.HTTPError:
        pass
    return []


def fetch_modules() -> list[dict]:
    try:
        response = _get("/api/modules", timeout=5.0)
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

    response = _post(
        "/api/transcribe",
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
    response = _post("/api/transcripts", json=payload, timeout=30.0)
    _raise_for_status(response)
    return response.json()


def upload_transcript_text(file_bytes: bytes, filename: str, title: str | None = None) -> dict:
    response = _post(
        "/api/transcripts/upload",
        files={"file": (filename, file_bytes)},
        data={"title": title or filename},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def update_transcript_speakers(transcript_id: str, speakers: list[dict]) -> dict:
    response = _patch(
        f"/api/transcripts/{transcript_id}/speakers",
        json={"speakers": speakers},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def update_transcript_turns(transcript_id: str, turns: list[dict]) -> dict:
    response = _patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={"turns": turns},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def rebuild_transcript_evidence(transcript_id: str) -> dict:
    response = _post(
        f"/api/transcripts/{transcript_id}/evidence/rebuild",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def mark_transcript_ready(transcript_id: str, *, skip_review: bool = False) -> dict:
    response = _post(
        f"/api/transcripts/{transcript_id}/ready",
        json={"skip_review": skip_review},
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def delete_transcript(transcript_id: str) -> None:
    response = _delete(f"/api/transcripts/{transcript_id}", timeout=30.0)
    _raise_for_status(response)


def record_audit_event(
    event: str,
    *,
    transcript_id: str | None = None,
    workflow_run_id: str | None = None,
    export_format: str | None = None,
) -> None:
    payload = {
        "event": event,
        "transcript_id": transcript_id,
        "workflow_run_id": workflow_run_id,
        "export_format": export_format,
    }
    try:
        response = _post("/api/audit/events", json=payload, timeout=5.0)
        if response.status_code >= 400:
            return
    except httpx.HTTPError:
        return


def process_audio(
    file_bytes: bytes,
    filename: str,
    workflow_id: str,
    model: str | None = None,
) -> dict:
    data: dict[str, str] = {"workflow_id": workflow_id}
    if model:
        data["model"] = model
    response = _post(
        "/api/process",
        files={"file": (filename, file_bytes)},
        data=data,
        timeout=PROCESS_TIMEOUT,
    )
    _raise_for_status(response)
    return response.json()


def run_workflow(
    transcript_id: str,
    workflow_id: str,
    model: str | None = None,
    *,
    background: bool | None = None,
) -> dict:
    payload: dict[str, object] = {"transcript_id": transcript_id, "model": model}
    if background is not None:
        payload["background"] = background
    response = _post(
        f"/api/workflows/{workflow_id}/run",
        json=payload,
        timeout=WORKFLOW_TIMEOUT,
    )
    _raise_for_status(response)
    return response.json()


def get_workflow_run(run_id: str) -> dict:
    response = _get(f"/api/workflow-runs/{run_id}", timeout=30.0)
    _raise_for_status(response)
    return response.json()


def get_workflow_synthesis(run_id: str) -> dict:
    response = _get(f"/api/workflow-runs/{run_id}/synthesis", timeout=30.0)
    _raise_for_status(response)
    return response.json()


def fetch_exploration_findings(run_id: str) -> list[dict]:
    response = _get(
        f"/api/workflow-runs/{run_id}/exploration/findings",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json().get("findings", [])


def fetch_finding_drilldown(run_id: str, finding_key: str) -> dict:
    response = _get(
        f"/api/workflow-runs/{run_id}/exploration/findings/{finding_key}",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_cross_module_alignment(run_id: str) -> dict:
    response = _get(
        f"/api/workflow-runs/{run_id}/exploration/cross-module",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_knowledge_graph(run_id: str) -> dict:
    response = _get(
        f"/api/workflow-runs/{run_id}/exploration/knowledge-graph",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json()


def fetch_transcript_workflow_runs(transcript_id: str) -> list[dict]:
    response = _get(
        f"/api/transcripts/{transcript_id}/workflow-runs",
        timeout=30.0,
    )
    _raise_for_status(response)
    return response.json().get("workflow_runs", [])


def compare_workflow_runs(workflow_run_ids: list[str]) -> dict:
    response = _post(
        "/api/exploration/compare",
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
    response = _post(
        f"/api/workflow-runs/{run_id}/exploration/ask",
        json=payload,
        timeout=120.0,
    )
    _raise_for_status(response)
    return response.json()
