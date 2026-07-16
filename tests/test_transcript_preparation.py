"""Transcript preparation workspace API (v0.7 P2)."""

from fastapi.testclient import TestClient

from backend.main import app
from config.settings import settings


def test_update_turns_excludes_and_regenerates_quote_ids(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", False)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Hello there.\nPerson B: Hi back.\nPerson A: Follow up.",
            "source_type": "paste",
        },
    )
    assert created.status_code == 200
    data = created.json()
    transcript_id = data["transcript"]["id"]
    assert len(data["evidence_quotes"]) == 3
    assert data["transcript"]["analysis_ready"] is False

    turn_b = next(t for t in data["turns"] if "Hi back" in t["text"])
    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={
            "turns": [
                {
                    "id": turn_b["id"],
                    "excluded_from_analysis": True,
                }
            ]
        },
    )
    assert patched.status_code == 200
    body = patched.json()
    assert len(body["evidence_quotes"]) == 2
    assert body["evidence_quotes"][0]["quote_id"] == "Q001"
    assert body["evidence_quotes"][1]["quote_id"] == "Q002"
    assert body["transcript"]["analysis_ready"] is False
    excluded = next(t for t in body["turns"] if t["id"] == turn_b["id"])
    assert excluded["excluded_from_analysis"] is True


def test_mark_ready_gates_workflow_without_auto_mark(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", False)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: Hello.\nPerson B: Hi.", "source_type": "paste"},
    )
    transcript_id = created.json()["transcript"]["id"]

    blocked = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": transcript_id, "background": False},
    )
    assert blocked.status_code == 422

    ready = client.post(
        f"/api/transcripts/{transcript_id}/ready",
        json={"skip_review": False},
    )
    assert ready.status_code == 200
    assert ready.json()["transcript"]["analysis_ready"] is True
