"""Phase 005 — evidence snapshots and transcript versioning."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.db.models import EvidenceQuoteRow, TranscriptVersionRow, WorkflowRunRow
from backend.domain.enums import WorkflowRunStatus
from backend.main import app
from backend.repositories.workflow_run_repository import utc_now
from backend.services.transcript_service import transcript_service
from backend.services.workflow_engine import workflow_engine
from config.settings import settings

ROOT = Path(__file__).resolve().parents[1]


def test_phase_005_docs_exist() -> None:
    phase = ROOT / "docs" / "planning" / "phases" / "005_v2_1_evidence_snapshots_and_versioning.md"
    design = ROOT / "docs" / "developer" / "evidence_snapshot_versioning_design.md"
    assert phase.is_file()
    assert design.is_file()


def test_ingest_creates_version_one(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", False)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Hello there.\nPerson B: Hi back.",
            "source_type": "paste",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["transcript"]["current_version_id"]
    assert body["transcript"]["current_version_number"] == 1
    assert body["evidence_quotes"]
    assert all(q.get("transcript_version_id") for q in body["evidence_quotes"])
    assert body["evidence_quotes"][0]["transcript_version_id"] == body["transcript"][
        "current_version_id"
    ]


def test_edit_before_analysis_keeps_single_version(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", False)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Hello there.\nPerson B: Hi back.\nPerson A: Follow up.",
            "source_type": "paste",
        },
    )
    data = created.json()
    transcript_id = data["transcript"]["id"]
    version_id = data["transcript"]["current_version_id"]
    turn_b = next(t for t in data["turns"] if "Hi back" in t["text"])

    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={"turns": [{"id": turn_b["id"], "excluded_from_analysis": True}]},
    )
    assert patched.status_code == 200
    body = patched.json()
    assert body["transcript"]["current_version_id"] == version_id
    assert body["transcript"]["current_version_number"] == 1
    assert len(body["evidence_quotes"]) == 2

    with get_session() as session:
        versions = session.query(TranscriptVersionRow).filter_by(
            transcript_id=transcript_id
        ).all()
        assert len(versions) == 1
        quote_count = session.query(EvidenceQuoteRow).filter_by(
            transcript_id=transcript_id
        ).count()
        assert quote_count == 2


def test_old_report_evidence_survives_transcript_edit(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Original quote text.\nPerson B: Reply here.",
            "source_type": "paste",
        },
    )
    assert created.status_code == 200
    data = created.json()
    transcript_id = data["transcript"]["id"]
    version_v1 = data["transcript"]["current_version_id"]
    q001_v1 = next(q for q in data["evidence_quotes"] if q["quote_id"] == "Q001")
    assert "Original quote text" in q001_v1["text"]

    # Bind a completed workflow run to version 1 (simulates finished analysis).
    run = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    with get_session() as session:
        row = session.get(WorkflowRunRow, run.id)
        assert row is not None
        row.status = WorkflowRunStatus.COMPLETED.value
        row.completed_at = utc_now().replace(tzinfo=None)
        row.transcript_version_id = version_v1
        session.flush()

    turn_a = next(t for t in data["turns"] if "Original quote text" in t["text"])
    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={
            "turns": [
                {"id": turn_a["id"], "text": "Completely rewritten quote text."}
            ]
        },
    )
    assert patched.status_code == 200
    current = patched.json()
    assert current["transcript"]["current_version_number"] == 2
    assert current["transcript"]["current_version_id"] != version_v1
    q001_current = next(
        q for q in current["evidence_quotes"] if q["quote_id"] == "Q001"
    )
    assert "Completely rewritten" in q001_current["text"]

    # Historical version still has original text for Q001.
    historical = client.get(
        f"/api/transcripts/{transcript_id}",
        params={"version_id": version_v1},
    )
    assert historical.status_code == 200
    hist_body = historical.json()
    q001_hist = next(
        q for q in hist_body["evidence_quotes"] if q["quote_id"] == "Q001"
    )
    assert q001_hist["text"] == q001_v1["text"]
    assert "Original quote text" in q001_hist["text"]

    # Direct service check: old version quotes unchanged in DB.
    v1_bundle = transcript_service.get_for_version(transcript_id, version_v1)
    assert v1_bundle.evidence_quotes[0].text == q001_v1["text"]

    with get_session() as session:
        v1_quotes = (
            session.query(EvidenceQuoteRow)
            .filter_by(transcript_version_id=version_v1)
            .all()
        )
        assert any("Original quote text" in q.text for q in v1_quotes)


def test_edit_during_queued_run_preserves_bound_version_evidence(monkeypatch) -> None:
    """Queued/in-flight runs bind a version; edits must not rewrite that evidence."""
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Bound quote text.\nPerson B: Reply.",
            "source_type": "paste",
        },
    )
    assert created.status_code == 200
    data = created.json()
    transcript_id = data["transcript"]["id"]
    version_v1 = data["transcript"]["current_version_id"]
    q001_v1 = next(q for q in data["evidence_quotes"] if q["quote_id"] == "Q001")
    assert "Bound quote text" in q001_v1["text"]

    # Create a queued run bound to V1 (no completion yet — the prior bug path).
    run = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    assert run.status == WorkflowRunStatus.CREATED.value
    assert run.transcript_version_id == version_v1

    turn_a = next(t for t in data["turns"] if "Bound quote text" in t["text"])
    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={
            "turns": [
                {"id": turn_a["id"], "text": "Rewritten while analysis still queued."}
            ]
        },
    )
    assert patched.status_code == 200
    current = patched.json()
    assert current["transcript"]["current_version_number"] == 2
    assert current["transcript"]["current_version_id"] != version_v1

    historical = client.get(
        f"/api/transcripts/{transcript_id}",
        params={"version_id": version_v1},
    )
    assert historical.status_code == 200
    q001_hist = next(
        q for q in historical.json()["evidence_quotes"] if q["quote_id"] == "Q001"
    )
    assert q001_hist["text"] == q001_v1["text"]
    assert "Bound quote text" in q001_hist["text"]

    with get_session() as session:
        row = session.get(WorkflowRunRow, run.id)
        assert row is not None
        assert row.transcript_version_id == version_v1
        v1_quotes = (
            session.query(EvidenceQuoteRow)
            .filter_by(transcript_version_id=version_v1)
            .all()
        )
        assert any("Bound quote text" in q.text for q in v1_quotes)


def test_edit_during_running_run_preserves_bound_version_evidence(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Running quote text.\nPerson B: Reply.",
            "source_type": "paste",
        },
    )
    data = created.json()
    transcript_id = data["transcript"]["id"]
    version_v1 = data["transcript"]["current_version_id"]
    q001_v1 = next(q for q in data["evidence_quotes"] if q["quote_id"] == "Q001")

    run = workflow_engine.create_run("quick_review", transcript_id, queued=False)
    assert run.status == WorkflowRunStatus.RUNNING_MODULES.value
    assert run.transcript_version_id == version_v1

    turn_a = next(t for t in data["turns"] if "Running quote text" in t["text"])
    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={
            "turns": [
                {"id": turn_a["id"], "text": "Rewritten while modules still running."}
            ]
        },
    )
    assert patched.status_code == 200
    assert patched.json()["transcript"]["current_version_id"] != version_v1

    hist = transcript_service.get_for_version(transcript_id, version_v1)
    assert hist.evidence_quotes[0].text == q001_v1["text"]


def test_reanalysis_binds_latest_version(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: First version text.\nPerson B: Answer.",
            "source_type": "paste",
        },
    )
    data = created.json()
    transcript_id = data["transcript"]["id"]
    version_v1 = data["transcript"]["current_version_id"]

    run1 = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    assert run1.transcript_version_id == version_v1
    with get_session() as session:
        row = session.get(WorkflowRunRow, run1.id)
        assert row is not None
        row.status = WorkflowRunStatus.COMPLETED.value
        row.completed_at = utc_now().replace(tzinfo=None)
        session.flush()

    turn = data["turns"][0]
    patched = client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={"turns": [{"id": turn["id"], "text": "Second version text now."}]},
    )
    assert patched.status_code == 200
    version_v2 = patched.json()["transcript"]["current_version_id"]
    assert version_v2 != version_v1

    # Re-approve after edit (cleared ready).
    ready = client.post(f"/api/transcripts/{transcript_id}/ready", json={})
    assert ready.status_code == 200
    latest_version = ready.json()["transcript"]["current_version_id"]

    run2 = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    assert run2.transcript_version_id == latest_version
    assert run2.transcript_version_id != version_v1

    fetched = workflow_engine.get(run1.id)
    assert fetched.transcript_version_id == version_v1
    assert fetched.transcript_is_stale is True

    fetched2 = workflow_engine.get(run2.id)
    assert fetched2.transcript_is_stale is False


def test_quote_id_collision_is_version_scoped(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Alpha text.\nPerson B: Bravo.",
            "source_type": "paste",
        },
    )
    data = created.json()
    transcript_id = data["transcript"]["id"]
    v1 = data["transcript"]["current_version_id"]

    run = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    with get_session() as session:
        row = session.get(WorkflowRunRow, run.id)
        assert row is not None
        row.status = WorkflowRunStatus.COMPLETED.value
        row.completed_at = utc_now().replace(tzinfo=None)
        session.flush()

    turn = data["turns"][0]
    client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={"turns": [{"id": turn["id"], "text": "Zulu text after edit."}]},
    )
    current = client.get(f"/api/transcripts/{transcript_id}").json()
    v2 = current["transcript"]["current_version_id"]

    hist = client.get(
        f"/api/transcripts/{transcript_id}", params={"version_id": v1}
    ).json()
    q_hist = next(q for q in hist["evidence_quotes"] if q["quote_id"] == "Q001")
    q_cur = next(q for q in current["evidence_quotes"] if q["quote_id"] == "Q001")
    assert q_hist["text"] != q_cur["text"]
    assert q_hist["transcript_version_id"] == v1
    assert q_cur["transcript_version_id"] == v2
    assert "Alpha" in q_hist["text"]
    assert "Zulu" in q_cur["text"]


def test_workflow_run_api_exposes_version_and_stale(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": "Person A: Keep me.\nPerson B: Ok.",
            "source_type": "paste",
        },
    )
    data = created.json()
    transcript_id = data["transcript"]["id"]
    run = workflow_engine.create_run("quick_review", transcript_id, queued=True)
    with get_session() as session:
        row = session.get(WorkflowRunRow, run.id)
        assert row is not None
        row.status = WorkflowRunStatus.COMPLETED.value
        row.completed_at = utc_now().replace(tzinfo=None)
        session.flush()

    turn = data["turns"][0]
    client.patch(
        f"/api/transcripts/{transcript_id}/turns",
        json={"turns": [{"id": turn["id"], "text": "Changed after analysis."}]},
    )

    resp = client.get(f"/api/v1/workflow-runs/{run.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["transcript_version_id"]
    assert body["transcript_version_number"] == 1
    assert body["transcript_is_stale"] is True
    assert body["transcript_current_version_id"] != body["transcript_version_id"]
