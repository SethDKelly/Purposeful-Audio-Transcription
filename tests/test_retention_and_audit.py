from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.db.models import TranscriptRow
from backend.main import app
from backend.services.transcript_service import transcript_service
from config.settings import settings


def test_purge_expired_respects_retention(monkeypatch) -> None:
    monkeypatch.setattr(settings, "transcript_retention_days", 30)
    client = TestClient(app)

    fresh = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: fresh.", "source_type": "paste", "title": "fresh"},
    ).json()
    stale = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: stale.", "source_type": "paste", "title": "stale"},
    ).json()
    fresh_id = fresh["transcript"]["id"]
    stale_id = stale["transcript"]["id"]

    old = datetime.now(UTC) - timedelta(days=60)
    with get_session() as session:
        row = session.get(TranscriptRow, stale_id)
        assert row is not None
        row.created_at = old.replace(tzinfo=None)
        session.flush()

    purged = transcript_service.purge_expired()
    assert purged >= 1
    assert client.get(f"/api/transcripts/{stale_id}").status_code == 404
    assert client.get(f"/api/transcripts/{fresh_id}").status_code == 200


def test_purge_disabled_when_unset(monkeypatch) -> None:
    monkeypatch.setattr(settings, "transcript_retention_days", None)
    assert transcript_service.purge_expired() == 0


def test_audit_export_event() -> None:
    client = TestClient(app)
    create = client.post(
        "/api/transcripts",
        json={"raw_text": "Person A: Hello.", "source_type": "paste"},
    )
    tid = create.json()["transcript"]["id"]
    response = client.post(
        "/api/audit/events",
        json={
            "event": "transcript.export",
            "transcript_id": tid,
            "export_format": "md",
        },
    )
    assert response.status_code == 204


def test_audit_rejects_unknown_event() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/audit/events",
        json={"event": "not.allowed"},
    )
    assert response.status_code == 400
