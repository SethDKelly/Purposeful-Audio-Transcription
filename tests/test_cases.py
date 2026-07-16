"""Case data model API (v0.9 P1)."""

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.transcript_service import transcript_service
from backend.domain.enums import SourceType


def test_create_list_and_assign_case() -> None:
    client = TestClient(app)
    created = client.post("/api/cases", json={"title": "Couple A", "notes": "Pilot"}).json()
    assert created["title"] == "Couple A"
    case_id = created["id"]

    listed = client.get("/api/cases").json()
    assert any(item["id"] == case_id for item in listed["cases"])

    bundle = transcript_service.ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="Session 1",
    )
    assign = client.patch(
        f"/api/transcripts/{bundle.transcript.id}/case",
        json={
            "case_id": case_id,
            "session_label": "Session 1",
            "session_date": "2026-01-15T10:00:00",
        },
    )
    assert assign.status_code == 200
    assert assign.json()["case_id"] == case_id

    detail = client.get(f"/api/cases/{case_id}").json()
    assert len(detail["transcripts"]) == 1
    assert detail["transcripts"][0]["session_label"] == "Session 1"

    fetched = client.get(f"/api/transcripts/{bundle.transcript.id}").json()
    assert fetched["transcript"]["case_id"] == case_id
    assert fetched["transcript"]["session_label"] == "Session 1"


def test_delete_case_unlinks_transcripts() -> None:
    client = TestClient(app)
    case_id = client.post("/api/cases", json={"title": "Temp"}).json()["id"]
    bundle = transcript_service.ingest(
        "Person A: Bye.\nPerson B: Bye.",
        source_type=SourceType.PASTE,
        title="Session X",
    )
    client.patch(
        f"/api/transcripts/{bundle.transcript.id}/case",
        json={"case_id": case_id, "session_label": "X"},
    )
    assert client.delete(f"/api/cases/{case_id}").status_code == 204
    fetched = client.get(f"/api/transcripts/{bundle.transcript.id}").json()
    assert fetched["transcript"]["case_id"] is None
