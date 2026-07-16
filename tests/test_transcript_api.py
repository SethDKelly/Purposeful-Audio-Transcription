from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.db.base import get_session
from backend.db.models import (
    EvidenceQuoteRow,
    ModuleRunRow,
    SpeakerRow,
    SynthesisReportRow,
    TranscriptRow,
    TurnRow,
    WorkflowRunRow,
)
from backend.core.module_registry import ModuleRegistry
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import transcript_service
from tests.test_workflow_engine import _module_llm_response


def test_create_and_get_transcript() -> None:
    client = TestClient(app)
    payload = {
        "raw_text": "Person A: Hello there.\nPerson B: Hi back.",
        "source_type": "paste",
        "title": "Test conversation",
    }
    create_response = client.post("/api/transcripts", json=payload)
    assert create_response.status_code == 200
    data = create_response.json()
    assert data["transcript"]["title"] == "Test conversation"
    assert len(data["speakers"]) == 2
    assert len(data["turns"]) == 2
    assert data["evidence_quotes"][0]["quote_id"] == "Q001"

    transcript_id = data["transcript"]["id"]
    get_response = client.get(f"/api/transcripts/{transcript_id}")
    assert get_response.status_code == 200
    assert get_response.json()["evidence_quotes"][1]["quote_id"] == "Q002"


def test_update_speakers() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: Hello.", "source_type": "paste"},
    )
    data = create_response.json()
    transcript_id = data["transcript"]["id"]
    speaker_id = data["speakers"][0]["id"]

    patch_response = client.patch(
        f"/api/transcripts/{transcript_id}/speakers",
        json={"speakers": [{"id": speaker_id, "display_name": "Alex"}]},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["speakers"][0]["display_name"] == "Alex"


def test_delete_transcript_cascade(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(
        registry=ModuleRegistry(), llm=mock_llm, transcripts=transcript_service
    )
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    client = TestClient(app)
    create_response = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Hello there.\nPerson B: Hi back.",
            "source_type": "paste",
        },
    )
    transcript_id = create_response.json()["transcript"]["id"]

    run_response = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": transcript_id, "model": "test-model"},
    )
    assert run_response.status_code == 200
    run_id = run_response.json()["id"]

    delete_response = client.delete(f"/api/transcripts/{transcript_id}")
    assert delete_response.status_code == 204

    assert client.get(f"/api/transcripts/{transcript_id}").status_code == 404
    assert client.get(f"/api/workflow-runs/{run_id}").status_code == 404

    with get_session() as session:
        assert session.get(TranscriptRow, transcript_id) is None
        assert not session.scalars(
            select(WorkflowRunRow).where(WorkflowRunRow.transcript_id == transcript_id)
        ).first()
        assert not session.scalars(
            select(ModuleRunRow).where(ModuleRunRow.transcript_id == transcript_id)
        ).first()
        assert not session.scalars(
            select(SynthesisReportRow).where(SynthesisReportRow.workflow_run_id == run_id)
        ).first()
        assert not session.scalars(
            select(EvidenceQuoteRow).where(EvidenceQuoteRow.transcript_id == transcript_id)
        ).first()
        assert not session.scalars(
            select(TurnRow).where(TurnRow.transcript_id == transcript_id)
        ).first()
        assert not session.scalars(
            select(SpeakerRow).where(SpeakerRow.transcript_id == transcript_id)
        ).first()


def test_delete_transcript_not_found() -> None:
    client = TestClient(app)
    response = client.delete("/api/transcripts/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
