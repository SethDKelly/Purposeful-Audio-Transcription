"""Phase 003 — email OTP auth and resource ownership."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.db.models import LoginCodeRow
from backend.main import app
from backend.services import email_delivery as email_mod
from config.settings import settings


class _CaptureEmail:
    def __init__(self) -> None:
        self.last_email: str | None = None
        self.last_code: str | None = None

    def send_login_code(self, *, email: str, code: str) -> None:
        self.last_email = email
        self.last_code = code


@pytest.fixture
def capture_email(monkeypatch: pytest.MonkeyPatch) -> _CaptureEmail:
    capture = _CaptureEmail()
    monkeypatch.setattr(email_mod, "email_delivery", capture)
    monkeypatch.setattr("backend.services.auth_service.email_delivery", capture)
    return capture


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, capture: _CaptureEmail, email: str = "pilot@example.com") -> dict:
    r = client.post("/api/v1/auth/request-code", json={"email": email})
    assert r.status_code == 200
    assert capture.last_code
    v = client.post(
        "/api/v1/auth/verify-code",
        json={"email": email, "code": capture.last_code},
    )
    assert v.status_code == 200
    return v.json()


def test_request_and_verify_login_code(client: TestClient, capture_email: _CaptureEmail) -> None:
    me = _login(client, capture_email)
    assert me["email"] == "pilot@example.com"
    assert me["id"]
    profile = client.get("/api/v1/auth/me")
    assert profile.status_code == 200
    assert profile.json()["email"] == "pilot@example.com"


def test_expired_login_code_rejected(
    client: TestClient, capture_email: _CaptureEmail
) -> None:
    email = "expire@example.com"
    assert client.post("/api/v1/auth/request-code", json={"email": email}).status_code == 200
    with get_session() as session:
        from sqlalchemy import select

        row = session.scalars(
            select(LoginCodeRow).where(LoginCodeRow.email == email)
        ).one()
        row.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
        session.flush()
    bad = client.post(
        "/api/v1/auth/verify-code",
        json={"email": email, "code": capture_email.last_code},
    )
    assert bad.status_code == 401


def test_reused_login_code_rejected(
    client: TestClient, capture_email: _CaptureEmail
) -> None:
    email = "reuse@example.com"
    _login(client, capture_email, email=email)
    again = client.post(
        "/api/v1/auth/verify-code",
        json={"email": email, "code": capture_email.last_code},
    )
    assert again.status_code == 401


def test_logout_revokes_session(client: TestClient, capture_email: _CaptureEmail) -> None:
    _login(client, capture_email, email="logout@example.com")
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_cross_user_transcript_and_case_denied(
    client: TestClient, capture_email: _CaptureEmail
) -> None:
    user_a = _login(client, capture_email, email="alice@example.com")
    created = client.post(
        "/api/v1/transcripts",
        json={"raw_text": "Alice: hello\nBob: hi", "source_type": "paste", "title": "A"},
    )
    assert created.status_code == 200
    transcript_id = created.json()["transcript"]["id"]

    case = client.post("/api/v1/cases", json={"title": "Alice case"})
    assert case.status_code == 200
    case_id = case.json()["id"]

    client.post("/api/v1/auth/logout")
    _login(client, capture_email, email="bob@example.com")

    denied_t = client.get(f"/api/v1/transcripts/{transcript_id}")
    assert denied_t.status_code == 403

    denied_c = client.get(f"/api/v1/cases/{case_id}")
    assert denied_c.status_code == 403

    # Owner can still access after re-login
    client.post("/api/v1/auth/logout")
    _login(client, capture_email, email="alice@example.com")
    assert client.get(f"/api/v1/transcripts/{transcript_id}").status_code == 200
    assert client.get(f"/api/v1/cases/{case_id}").status_code == 200
    assert user_a["email"] == "alice@example.com"


def test_cross_user_report_denied_via_workflow_run_owner(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "auto_mark_transcript_ready", True)
    _login(client, capture_email, email="owner@example.com")
    created = client.post(
        "/api/v1/transcripts",
        json={
            "raw_text": "Person A: hello there\nPerson B: hi back",
            "source_type": "paste",
            "title": "Owned",
        },
    )
    transcript_id = created.json()["transcript"]["id"]
    client.post(f"/api/v1/transcripts/{transcript_id}/ready", json={"skip_review": True})

    # Create a workflow run row owned by current user without executing modules
    from backend.db.models import WorkflowRunRow
    from backend.repositories.workflow_run_repository import utc_now
    import uuid

    run_id = str(uuid.uuid4())
    with get_session() as session:
        # fetch owner id
        from backend.db.models import UserRow
        from sqlalchemy import select

        owner = session.scalars(
            select(UserRow).where(UserRow.email == "owner@example.com")
        ).one()
        session.add(
            WorkflowRunRow(
                id=run_id,
                workflow_id="quick_review",
                transcript_id=transcript_id,
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

    client.post("/api/v1/auth/logout")
    _login(client, capture_email, email="intruder@example.com")
    denied = client.get(f"/api/v1/workflow-runs/{run_id}")
    assert denied.status_code == 403
    denied_report = client.get(f"/api/v1/reports/{run_id}")
    # report may 404 if no synthesis; ownership should still 403 first
    assert denied_report.status_code in {403, 404}


def test_session_auth_required_blocks_without_credentials(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "session_auth_required", True)
    monkeypatch.setattr(settings, "api_key", "")
    blocked = client.get("/api/v1/workflows")
    assert blocked.status_code == 401
    # Auth endpoints remain public
    assert client.post("/api/v1/auth/request-code", json={"email": "x@y.com"}).status_code == 200


def test_auth_rate_limit(client: TestClient, capture_email: _CaptureEmail, monkeypatch) -> None:
    monkeypatch.setattr(settings, "login_code_rate_limit_per_hour", 2)
    email = "rate@example.com"
    assert client.post("/api/v1/auth/request-code", json={"email": email}).status_code == 200
    assert client.post("/api/v1/auth/request-code", json={"email": email}).status_code == 200
    limited = client.post("/api/v1/auth/request-code", json={"email": email})
    assert limited.status_code == 400
