"""Phase 006 — worker atomic claim and operational safety."""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.domain.enums import WorkflowRunStatus
from backend.main import app
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_job_service import WorkflowJobService
from config.settings import settings
from tests.test_workflow_engine import (
    _build_engine,
    _ingest_golden,
    _module_llm_response,
)

ROOT = Path(__file__).resolve().parents[1]


def test_phase_006_doc_exists() -> None:
    phase = (
        ROOT
        / "docs"
        / "planning"
        / "phases"
        / "006_v2_1_worker_atomicity_and_operational_safety.md"
    )
    assert phase.is_file()
    text = phase.read_text(encoding="utf-8")
    assert "atomic" in text.lower()


def test_concurrent_workers_only_one_claims() -> None:
    mock_llm = MagicMock()
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)
    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )

    barrier = threading.Barrier(2)
    results: list[object] = []
    lock = threading.Lock()

    def _claim() -> None:
        barrier.wait(timeout=5)
        claimed = engine.claim_queued(run.id)
        with lock:
            results.append(claimed)

    threads = [threading.Thread(target=_claim) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    winners = [r for r in results if r is not None]
    losers = [r for r in results if r is None]
    assert len(results) == 2
    assert len(winners) == 1
    assert len(losers) == 1
    winner = winners[0]
    assert winner.status == WorkflowRunStatus.RUNNING_MODULES.value
    assert winner.attempt_count == 1

    current = engine.get(run.id)
    assert current.status == WorkflowRunStatus.RUNNING_MODULES.value
    assert current.attempt_count == 1


def test_canceled_job_is_not_claimed() -> None:
    mock_llm = MagicMock()
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)
    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    cancelled = engine.request_cancel(run.id)
    assert cancelled.status == WorkflowRunStatus.CANCELLED.value
    assert engine.claim_queued(run.id) is None


def test_claim_respects_cancel_requested_flag() -> None:
    """Even if status were still created, cancel_requested blocks claim."""
    mock_llm = MagicMock()
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)
    run = engine.create_run(
        "quick_review",
        bundle.transcript.id,
        model="test-model",
        queued=True,
    )
    with get_session() as session:
        current = engine._repository.get(session, run.id)
        current.cancel_requested = True
        # Leave status as created to isolate the cancel_requested predicate.
        current.status = WorkflowRunStatus.CREATED.value
        engine._repository.save(session, current)

    assert engine.claim_queued(run.id) is None


def test_retry_exhaustion_marks_failed(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_job_max_attempts", 2)
    monkeypatch.setattr(settings, "workflow_worker_enabled", True)
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
    assert claimed.attempt_count == 1

    # First failure: requeue.
    jobs._maybe_requeue(run.id, "simulated failure 1")
    requeued = engine.get(run.id)
    assert requeued.status == WorkflowRunStatus.CREATED.value
    assert requeued.attempt_count == 1

    claimed2 = engine.claim_queued(run.id)
    assert claimed2 is not None
    assert claimed2.attempt_count == 2

    # Second failure at max attempts: failed.
    jobs._maybe_requeue(run.id, "simulated failure 2")
    failed = engine.get(run.id)
    assert failed.status == WorkflowRunStatus.FAILED.value
    assert "Retry exhausted" in (failed.error_log or "")
    jobs.shutdown()


def test_stale_recovery_exhausts_retries(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_job_stale_seconds", 1)
    monkeypatch.setattr(settings, "workflow_job_max_attempts", 1)
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
    assert claimed.attempt_count == 1

    with get_session() as session:
        current = engine._repository.get(session, run.id)
        current.started_at = datetime.now(UTC) - timedelta(seconds=30)
        engine._repository.save(session, current)

    recovered = jobs.recover_stale(exclude_run_ids=set())
    assert recovered == 1
    failed = engine.get(run.id)
    assert failed.status == WorkflowRunStatus.FAILED.value
    assert "Stale recovery exhausted" in (failed.error_log or "")
    jobs.shutdown()


def test_queue_metrics_still_callable_after_atomic_claim(monkeypatch) -> None:
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

    stats_before = jobs.queue_stats()
    assert "queue_depth" in stats_before
    assert stats_before["queue_depth"] >= 1

    claimed = engine.claim_queued(run.id)
    assert claimed is not None

    stats_after = jobs.queue_stats()
    assert "queue_depth" in stats_after
    assert "running_count" in stats_after
    assert "worker_in_flight" in stats_after
    assert "worker_max_in_flight" in stats_after

    client = TestClient(app)
    api_stats = client.get("/api/queue/stats")
    assert api_stats.status_code == 200
    body = api_stats.json()
    assert "queue_depth" in body
    assert "oldest_queued_age_seconds" in body
    jobs.shutdown()
