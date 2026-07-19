"""Tests for workflow job cancel, timeout, and queue claim."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.domain.enums import SourceType, WorkflowRunStatus
from backend.main import app
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_job_service import WorkflowJobService
from config.settings import settings
from tests.test_workflow_engine import (
    FIXTURES,
    _build_engine,
    _ingest_golden,
    _module_llm_response,
)


def test_cancel_queued_workflow_via_api(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [_module_llm_response("relationship_conversation_analysis")]

    # Use real engine path through API with worker mode (queue only).
    client = TestClient(app)
    transcripts = TranscriptService()
    bundle = transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Cancel test",
    )
    transcripts.mark_ready(bundle.transcript.id)

    run_resp = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": bundle.transcript.id, "background": True, "model": "test"},
    )
    assert run_resp.status_code == 200
    run_id = run_resp.json()["id"]
    assert run_resp.json()["status"] == WorkflowRunStatus.CREATED.value

    cancel_resp = client.post(f"/api/workflow-runs/{run_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == WorkflowRunStatus.CANCELLED.value


def test_claim_queued_increments_attempt() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    assert run.status == WorkflowRunStatus.CREATED.value
    claimed = engine.claim_queued(run.id)
    assert claimed is not None
    assert claimed.attempt_count == 1
    assert claimed.status == WorkflowRunStatus.RUNNING_MODULES.value
    assert engine.claim_queued(run.id) is None


def test_engine_honors_cancel_between_modules(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    engine.claim_queued(run.id)

    original_check = engine._check_abort
    calls = {"n": 0}

    def cancel_after_first(workflow_run, started):
        calls["n"] += 1
        if calls["n"] >= 2:
            engine.request_cancel(workflow_run.id)
        original_check(workflow_run, started)

    monkeypatch.setattr(engine, "_check_abort", cancel_after_first)
    result = engine.run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        run_id=run.id,
    )
    assert result.status == WorkflowRunStatus.CANCELLED.value


def test_job_service_poll_claims_created(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    jobs = WorkflowJobService(engine=engine, max_workers=1)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    started = jobs.poll_once()
    assert started == 1
    # Allow thread to finish
    import time

    for _ in range(50):
        current = engine.get(run.id)
        if current.status in {
            WorkflowRunStatus.COMPLETED.value,
            WorkflowRunStatus.FAILED.value,
            WorkflowRunStatus.CANCELLED.value,
        }:
            break
        time.sleep(0.05)
    assert engine.get(run.id).status == WorkflowRunStatus.COMPLETED.value
    jobs.shutdown()


def test_poll_respects_max_claim_per_poll(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
    monkeypatch.setattr(settings, "workflow_worker_max_claim_per_poll", 1)
    monkeypatch.setattr(settings, "workflow_worker_max_in_flight", 4)
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ] * 4
    engine = _build_engine(mock_llm)
    jobs = WorkflowJobService(engine=engine, max_workers=4)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    for _ in range(2):
        engine.create_run(
            "quick_review",
            bundle.transcript.id,
            model="test-model",
            queued=True,
        )

    assert jobs.poll_once() == 1
    assert len(engine.list_queued()) == 1
    jobs.shutdown()


def test_poll_respects_max_in_flight(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
    monkeypatch.setattr(settings, "workflow_worker_max_claim_per_poll", 2)
    monkeypatch.setattr(settings, "workflow_worker_max_in_flight", 1)

    engine = MagicMock()
    hold = MagicMock()
    hold.id = "run-a"
    hold.workflow_id = "quick_review"
    hold.transcript_id = "t1"
    hold.model_used = "test"
    queued = MagicMock()
    queued.id = "run-b"
    engine.list_queued.side_effect = [[hold], [queued]]
    engine.claim_queued.side_effect = [hold, None]

    jobs = WorkflowJobService(engine=engine, max_workers=1)

    def _block(*_a, **_k):
        import time

        time.sleep(0.3)
        return hold

    jobs._run_claimed = _block  # type: ignore[method-assign]
    assert jobs.poll_once() == 1
    assert jobs.in_flight_count == 1
    assert jobs.poll_once() == 0
    import time

    time.sleep(0.4)
    assert jobs.in_flight_count == 0
    jobs.shutdown()


def test_queue_stats_and_failed_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
    client = TestClient(app)
    stats = client.get("/api/queue/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert "queue_depth" in body
    assert "oldest_queued_age_seconds" in body
    failed = client.get("/api/queue/failed")
    assert failed.status_code == 200
    assert "runs" in failed.json()


def test_recover_stale_requeues(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_job_stale_seconds", 1)
    monkeypatch.setattr(settings, "workflow_job_max_attempts", 3)
    mock_llm = MagicMock()
    engine = _build_engine(mock_llm)
    jobs = WorkflowJobService(engine=engine, max_workers=1)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)
    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    claimed = engine.claim_queued(run.id)
    assert claimed is not None
    from datetime import UTC, datetime, timedelta

    from backend.db.base import get_session

    with get_session() as session:
        current = engine._repository.get(session, run.id)
        current.started_at = datetime.now(UTC) - timedelta(seconds=30)
        engine._repository.save(session, current)

    recovered = jobs.recover_stale(exclude_run_ids=set())
    assert recovered == 1
    assert engine.get(run.id).status == WorkflowRunStatus.CREATED.value
    jobs.shutdown()
