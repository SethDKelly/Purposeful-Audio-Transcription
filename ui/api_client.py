"""Shared API client helpers for the Streamlit UI."""

from collections.abc import Iterator

import httpx

from config.settings import settings

API_BASE = f"http://{settings.api_host}:{settings.api_port}"
TRANSCRIBE_TIMEOUT = 600.0
ANALYZE_TIMEOUT = 600.0
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


def fetch_purposes() -> list[dict]:
    try:
        response = httpx.get(f"{API_BASE}/api/purposes", timeout=5.0)
        if response.status_code == 200:
            return response.json().get("purposes", [])
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


def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    response = httpx.post(
        f"{API_BASE}/api/transcribe",
        files={"file": (filename, file_bytes)},
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
    _raise_for_status(response)
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
                import json

                detail = json.loads(error_body).get("detail", error_body)
            except Exception:
                detail = error_body
            raise RuntimeError(detail)
        yield from response.iter_text()


def process_audio(
    file_bytes: bytes,
    filename: str,
    purpose_id: str | None = None,
    workflow_id: str | None = None,
    model: str | None = None,
) -> dict:
    data: dict[str, str] = {}
    if purpose_id:
        data["purpose_id"] = purpose_id
    if workflow_id:
        data["workflow_id"] = workflow_id
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
