"""Critical correctness: ownership gaps, handoff replay, worker resume CAS."""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.db.base import get_session
from backend.db.models import UserRow, WorkflowRunRow
from backend.domain.enums import WorkflowRunStatus
from backend.main import app
from backend.repositories.workflow_run_repository import utc_now
from backend.services import email_delivery as email_mod
from backend.services.power_service import (
    consume_handoff_nonce,
    mint_handoff_token,
)
from config.settings import settings
from tests.test_phase_003_email_auth import _CaptureEmail, _login
from tests.test_workflow_engine import _build_engine, _ingest_golden
from backend.services.transcript_service import TranscriptService


@pytest.fixture
def capture_email(monkeypatch: pytest.MonkeyPatch) -> _CaptureEmail:
    capture = _CaptureEmail()
    monkeypatch.setattr(email_mod, "email_delivery", capture)
    monkeypatch.setattr("backend.services.auth_service.email_delivery", capture)
    return capture


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _seed_owned_run(owner_email: str) -> tuple[str, str]:
    """Return (transcript_id, run_id) owned by owner_email (must already exist)."""
    with get_session() as session:
        owner = session.scalars(
            select(UserRow).where(UserRow.email == owner_email)
        ).one()
        tid = str(uuid.uuid4())
        from backend.db.models import TranscriptRow

        session.add(
            TranscriptRow(
                id=tid,
                title="owned",
                raw_text="A: hi\nB: yo",
                source_type="paste",
                created_at=utc_now(),
                owner_user_id=owner.id,
            )
        )
        run_id = str(uuid.uuid4())
        session.add(
            WorkflowRunRow(
                id=run_id,
                workflow_id="quick_review",
                transcript_id=tid,
                status="completed",
                started_at=utc_now(),
                completed_at=utc_now(),
                cancel_requested=False,
                attempt_count=1,
                safety_mode=False,
                owner_user_id=owner.id,
            )
        )
        session.flush()
    return tid, run_id


def test_legacy_api_blocked_for_non_admin_session(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "session_auth_required", True)
    monkeypatch.setattr(settings, "api_key", "")
    _login(client, capture_email, email="user@example.com")
    # Legacy route would otherwise bypass ownership.
    blocked = client.get("/api/cases")
    assert blocked.status_code == 403
    # Product v1 remains available.
    assert client.get("/api/v1/cases").status_code == 200


def test_v1_knowledge_graph_enforces_ownership(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "session_auth_required", True)
    monkeypatch.setattr(settings, "api_key", "")
    _login(client, capture_email, email="owner@example.com")
    _tid, run_id = _seed_owned_run("owner@example.com")
    client.post("/api/v1/auth/logout")
    _login(client, capture_email, email="intruder@example.com")
    denied = client.get(f"/api/v1/workflow-runs/{run_id}/knowledge-graph")
    assert denied.status_code == 403
    denied_findings = client.get(f"/api/v1/workflow-runs/{run_id}/findings")
    assert denied_findings.status_code == 403


def test_handoff_token_is_single_use(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "power_handoff_secret", "test-secret")
    uid = str(uuid.uuid4())
    with get_session() as session:
        session.add(
            UserRow(
                id=uid,
                email="handoff-once@example.com",
                display_name="H",
                created_at=utc_now(),
                is_active=True,
                is_admin=False,
            )
        )
        session.flush()
    token = mint_handoff_token(user_id=uid, email="handoff-once@example.com")
    first = client.post("/api/v1/ops/power/handoff", json={"token": token})
    assert first.status_code == 200
    client.post("/api/v1/auth/logout")
    second = client.post("/api/v1/ops/power/handoff", json={"token": token})
    assert second.status_code == 401


def test_consume_handoff_nonce_rejects_replay() -> None:
    nonce = uuid.uuid4().hex
    assert consume_handoff_nonce(nonce) is True
    assert consume_handoff_nonce(nonce) is False


def test_concurrent_resume_claim_only_one_wins() -> None:
    from unittest.mock import MagicMock

    engine = _build_engine(MagicMock())
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
    started_at = claimed.started_at

    barrier = threading.Barrier(2)
    results: list[object] = []
    lock = threading.Lock()

    def _resume() -> None:
        barrier.wait(timeout=5)
        won = engine.claim_in_flight_for_resume(run.id, started_at)
        with lock:
            results.append(won)

    threads = [threading.Thread(target=_resume) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    winners = [r for r in results if r is not None]
    losers = [r for r in results if r is None]
    assert len(winners) == 1
    assert len(losers) == 1


def test_lambda_wake_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    import os
    import sys
    from pathlib import Path
    from unittest.mock import MagicMock

    monkeypatch.setenv("POWER_STATE_TABLE", "test-power-state")
    path = Path("infra/lambda/power_control/handler.py")
    spec = importlib.util.spec_from_file_location("power_control_handler", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    fake_boto3 = MagicMock()
    fake_boto3.resource.return_value.Table.return_value = MagicMock()
    fake_boto3.client.return_value = MagicMock()
    sys.modules["boto3"] = fake_boto3  # type: ignore[assignment]
    try:
        spec.loader.exec_module(mod)
        mod._get_power_state = lambda: {"state": "asleep"}  # type: ignore[method-assign]
        resp = mod.handle_wake({"body": "{}"})
        assert resp["statusCode"] == 401
        assert "token" in resp["body"].lower()
    finally:
        sys.modules.pop("boto3", None)
        # Avoid leaking a partially-initialized module on retry.
        sys.modules.pop("power_control_handler", None)
        os.environ.pop("POWER_STATE_TABLE", None)


def test_stale_recovery_cas_loses_after_resume_fence(monkeypatch) -> None:
    from unittest.mock import MagicMock

    monkeypatch.setattr(settings, "workflow_job_stale_seconds", 1)
    monkeypatch.setattr(settings, "workflow_job_max_attempts", 2)
    engine = _build_engine(MagicMock())
    from backend.services.workflow_job_service import WorkflowJobService

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

    with get_session() as session:
        current = engine._repository.get(session, run.id)
        current.started_at = datetime.now(UTC) - timedelta(seconds=60)
        engine._repository.save(session, current)
        stale_started = current.started_at

    # Worker A fences the run for resume (bumps started_at).
    fenced = engine.claim_in_flight_for_resume(run.id, stale_started)
    assert fenced is not None

    # Worker B's stale recovery still holding the old started_at must lose.
    recovered = jobs.recover_stale(exclude_run_ids=set())
    assert recovered == 0
    still = engine.get(run.id)
    assert still.status == WorkflowRunStatus.RUNNING_MODULES.value
    jobs.shutdown()
