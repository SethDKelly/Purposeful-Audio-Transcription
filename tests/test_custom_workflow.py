"""Tests for custom workflow builder (v1.0 P3)."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.domain.enums import SourceType
from backend.main import app
from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import workflow_registry
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_engine import WorkflowEngine, workflow_engine
from tests.test_workflow_engine import (
    FIXTURES,
    _ingest_golden,
    _module_llm_response,
)


def _ready_transcript() -> str:
    transcripts = TranscriptService()
    bundle = transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Custom workflow test",
    )
    transcripts.mark_ready(bundle.transcript.id)
    return bundle.transcript.id


def test_custom_workflow_run_via_api(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
    ]
    monkeypatch.setattr(
        workflow_engine,
        "_runner",
        ModuleRunner(
            registry=ModuleRegistry(),
            llm=mock_llm,
            transcripts=TranscriptService(),
        ),
    )

    client = TestClient(app)
    transcript_id = _ready_transcript()
    response = client.post(
        "/api/workflows/custom/run",
        json={
            "transcript_id": transcript_id,
            "modules": ["relationship_conversation_analysis", "nvc_analysis"],
            "name": "Quick pair",
            "model": "test-model",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["workflow_id"] == "custom:quick-pair"
    assert body["status"] == "completed"
    assert len(body["module_runs"]) == 2


def test_custom_workflow_rejects_unknown_module() -> None:
    client = TestClient(app)
    transcript_id = _ready_transcript()
    response = client.post(
        "/api/workflows/custom/run",
        json={
            "transcript_id": transcript_id,
            "modules": ["not_a_real_module"],
        },
    )
    assert response.status_code == 404


def test_custom_workflow_rejects_empty_modules() -> None:
    client = TestClient(app)
    transcript_id = _ready_transcript()
    response = client.post(
        "/api/workflows/custom/run",
        json={"transcript_id": transcript_id, "modules": []},
    )
    assert response.status_code == 400


def test_custom_workflow_meta_synthesis_must_be_last() -> None:
    client = TestClient(app)
    transcript_id = _ready_transcript()
    response = client.post(
        "/api/workflows/custom/run",
        json={
            "transcript_id": transcript_id,
            "modules": ["meta_synthesis", "nvc_analysis"],
        },
    )
    assert response.status_code == 400
    assert "last" in response.json()["detail"].lower()


def test_custom_workflow_engine_path() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = WorkflowEngine(
        workflows=workflow_registry,
        runner=ModuleRunner(
            registry=ModuleRegistry(),
            llm=mock_llm,
            transcripts=TranscriptService(),
        ),
        transcripts=TranscriptService(),
    )
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    from backend.services.custom_workflow_service import custom_workflow_service

    definition, workflow_id = custom_workflow_service.build_definition(
        modules=["relationship_conversation_analysis", "bias_epistemic_quality"],
        name="Engine custom",
    )
    assert workflow_id == "custom:engine-custom"
    assert len(definition.module_sequence) == 2

    run = engine.run(
        workflow_id=workflow_id,
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    assert run.status == "completed"
    assert run.workflow_id == workflow_id
