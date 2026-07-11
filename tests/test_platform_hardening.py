import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.db.base import _engine_kwargs
from backend.domain.enums import ModuleRunStatus, SourceType, WorkflowRunStatus
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_engine import WorkflowEngine
from backend.services.workflow_job_service import WorkflowJobService
from config.settings import settings

FIXTURES = Path(__file__).parent / "fixtures"


def _module_llm_response(module_id: str) -> str:
    registry = ModuleRegistry()
    module = registry.get(module_id)
    payload = json.loads(
        (FIXTURES / "sample_module_output.json").read_text(encoding="utf-8")
    )
    payload["module_id"] = module_id
    payload["module_version"] = module.config.version
    return f"```json\n{json.dumps(payload)}\n```"


def _build_engine(mock_llm) -> WorkflowEngine:
    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )
    return WorkflowEngine(
        workflows=WorkflowRegistry(),
        runner=runner,
        transcripts=TranscriptService(),
    )


def _ingest_golden(transcripts: TranscriptService):
    return transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Golden transcript",
    )


def test_settings_is_sqlite_default() -> None:
    assert settings.is_sqlite is True
    assert settings.api_auth_enabled is False


def test_engine_kwargs_postgresql(monkeypatch) -> None:
    monkeypatch.setattr(settings, "database_url", "postgresql+psycopg://localhost/rre")
    kwargs = _engine_kwargs()
    assert kwargs["pool_pre_ping"] is True
    assert kwargs["pool_size"] == settings.database_pool_size


def test_workflow_engine_resumes_completed_modules() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)

    workflow_run = engine.create_run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    engine._runner.run(
        module_id="relationship_conversation_analysis",
        transcript_id=bundle.transcript.id,
        model="test-model",
        workflow_run_id=workflow_run.id,
    )

    resumed = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
        run_id=workflow_run.id,
    )
    _, module_runs = engine.get_with_module_runs(resumed.id)

    assert resumed.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 3
    assert mock_llm.chat.call_count == 3


def test_workflow_job_service_resume_incomplete() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)
    workflow_run = engine.create_run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    job_service = WorkflowJobService(engine=engine, max_workers=1)
    try:
        queued = job_service.resume_incomplete()
        assert queued == 1
        future = job_service.submit_existing_run(
            workflow_id="quick_review",
            transcript_id=bundle.transcript.id,
            run_id=workflow_run.id,
            model="test-model",
        )
        completed = future.result(timeout=30)
        assert completed.status == WorkflowRunStatus.COMPLETED.value
    finally:
        job_service.shutdown()


def test_api_key_middleware_blocks_protected_routes(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "test-secret")

    client = TestClient(app)
    blocked = client.get("/api/workflows")
    assert blocked.status_code == 401

    allowed = client.get("/api/workflows", headers={"X-API-Key": "test-secret"})
    assert allowed.status_code == 200

    health = client.get("/api/health")
    assert health.status_code == 200
    payload = health.json()
    assert "cuda_available" in payload
    assert "whisper_device" in payload
    assert "diarization_device" in payload
    assert "whisper_compute_type" in payload


def test_health_reports_resolved_devices(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from backend.main import app

    monkeypatch.setattr(
        "backend.api.routes.health.cuda_available",
        lambda: True,
    )
    monkeypatch.setattr(
        "backend.api.routes.health.whisper_service.resolved_device",
        lambda: "cuda",
    )
    monkeypatch.setattr(
        "backend.api.routes.health.whisper_service.resolved_compute_type",
        lambda: "float16",
    )
    monkeypatch.setattr(
        "backend.api.routes.health.diarization_service.resolved_device",
        lambda: "cuda",
    )
    monkeypatch.setattr(
        "backend.api.routes.health.diarization_service.is_available",
        lambda: True,
    )

    client = TestClient(app)
    payload = client.get("/api/health").json()
    assert payload["cuda_available"] is True
    assert payload["whisper_device"] == "cuda"
    assert payload["diarization_device"] == "cuda"
    assert payload["whisper_compute_type"] == "float16"
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(registry=ModuleRegistry(), llm=mock_llm, transcripts=TranscriptService())
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    client = TestClient(app)
    transcript_response = client.post(
        "/api/transcripts",
        json={
            "raw_text": (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
            "source_type": "paste",
        },
    )
    transcript_id = transcript_response.json()["transcript"]["id"]

    run_response = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": transcript_id, "model": "test-model", "background": True},
    )
    assert run_response.status_code == 200
    run_id = run_response.json()["id"]

    final_status = None
    for _ in range(100):
        status_response = client.get(f"/api/workflow-runs/{run_id}")
        final_status = status_response.json()["status"]
        if final_status == WorkflowRunStatus.COMPLETED.value:
            break

    assert final_status == WorkflowRunStatus.COMPLETED.value


def test_api_base_url_override(monkeypatch):
    monkeypatch.setenv("RRE_API_BASE_URL", "http://alb.example.com")
    from config.settings import Settings

    cfg = Settings()
    assert cfg.api_base_url == "http://alb.example.com"
