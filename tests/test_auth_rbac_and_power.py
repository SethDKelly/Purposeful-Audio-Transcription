"""Auth RBAC, invite-only, SES provider, kill mode, power handoff."""

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.db.base import get_session
from backend.db.models import UserRow, WorkflowRunRow
from backend.main import app
from backend.repositories.workflow_run_repository import utc_now
from backend.services import email_delivery as email_mod
from backend.services.power_service import mint_handoff_token, parse_handoff_token
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings
from tests.test_phase_003_email_auth import _CaptureEmail, _login


@pytest.fixture
def capture_email(monkeypatch: pytest.MonkeyPatch) -> _CaptureEmail:
    capture = _CaptureEmail()
    monkeypatch.setattr(email_mod, "email_delivery", capture)
    monkeypatch.setattr("backend.services.auth_service.email_delivery", capture)
    return capture


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _seed_user(
    email: str,
    *,
    is_admin: bool = False,
    is_active: bool = True,
    user_id: str | None = None,
) -> str:
    uid = user_id or str(uuid.uuid4())
    with get_session() as session:
        session.add(
            UserRow(
                id=uid,
                email=email.lower(),
                display_name=email.split("@")[0],
                created_at=utc_now(),
                last_login_at=None,
                is_active=is_active,
                is_admin=is_admin,
            )
        )
        session.flush()
    return uid


def test_ses_email_delivery_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "email_delivery", "ses")
    monkeypatch.setattr(settings, "ses_from_email", "noreply@example.com")

    class _FakeSES:
        def __init__(self) -> None:
            self.sent = None

        def send_email(self, **kwargs):
            self.sent = kwargs
            return {"MessageId": "1"}

    fake = _FakeSES()

    class _FakeBoto3:
        def client(self, _name, region_name=None):
            return fake

    monkeypatch.setattr(email_mod, "boto3", _FakeBoto3())
    delivery = email_mod.SESEmailDelivery(
        region="us-east-2", from_address="noreply@example.com"
    )
    delivery.send_login_code(email="a@b.com", code="123456")
    assert fake.sent is not None
    assert fake.sent["Destination"]["ToAddresses"] == ["a@b.com"]


def test_invite_only_skips_unknown_email(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "auth_invite_only", True)
    r = client.post("/api/v1/auth/request-code", json={"email": "unknown@example.com"})
    assert r.status_code == 200
    assert capture_email.last_code is None


def test_invite_only_sends_for_seeded_user(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "auth_invite_only", True)
    _seed_user("pilot@example.com")
    r = client.post("/api/v1/auth/request-code", json={"email": "pilot@example.com"})
    assert r.status_code == 200
    assert capture_email.last_code


def test_admin_bypasses_ownership(
    client: TestClient, capture_email: _CaptureEmail, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "auth_invite_only", False)
    _login(client, capture_email, email="owner@example.com")
    created = client.post(
        "/api/v1/transcripts",
        json={"raw_text": "A: hi\nB: yo", "source_type": "paste", "title": "T"},
    )
    tid = created.json()["transcript"]["id"]
    client.post("/api/v1/auth/logout")

    _seed_user("admin@example.com", is_admin=True)
    # Force invite-only off so verify can use seeded admin; login helper requests code
    monkeypatch.setattr(settings, "auth_invite_only", False)
    # Ensure admin user exists before login — _login may create non-admin if missing;
    # update to admin after login path uses existing row
    with get_session() as session:
        row = session.scalars(
            select(UserRow).where(UserRow.email == "admin@example.com")
        ).one()
        row.is_admin = True
        session.flush()

    me = _login(client, capture_email, email="admin@example.com")
    assert me["is_admin"] is True
    assert client.get(f"/api/v1/transcripts/{tid}").status_code == 200


def test_seed_admin_email_constant() -> None:
    assert "ollioxenhomefree@gmail.com" in open(
        "alembic/versions/017_seed_admin_user.py", encoding="utf-8"
    ).read()


def test_handoff_token_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "power_handoff_secret", "test-secret")
    token = mint_handoff_token(user_id="u1", email="a@b.com")
    payload = parse_handoff_token(token)
    assert payload["user_id"] == "u1"
    assert payload["email"] == "a@b.com"


def test_handoff_endpoint_sets_cookie(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "power_handoff_secret", "test-secret")
    uid = _seed_user("handoff@example.com", is_admin=False)
    token = mint_handoff_token(user_id=uid, email="handoff@example.com")
    r = client.post("/api/v1/ops/power/handoff", json={"token": token})
    assert r.status_code == 200
    assert r.json()["email"] == "handoff@example.com"
    assert client.get("/api/v1/auth/me").status_code == 200


def test_kill_mode_cancels_all_long_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "kill_long_jobs_enabled", True)
    monkeypatch.setattr(settings, "kill_long_jobs_seconds", 1.0)

    from backend.db.models import TranscriptRow

    tid = str(uuid.uuid4())
    with get_session() as session:
        session.add(
            TranscriptRow(
                id=tid,
                title="kill",
                raw_text="A: hi",
                source_type="paste",
                created_at=utc_now(),
            )
        )
        session.flush()

    old_id = str(uuid.uuid4())
    young_id = str(uuid.uuid4())
    with get_session() as session:
        session.add(
            WorkflowRunRow(
                id=old_id,
                workflow_id="quick_review",
                transcript_id=tid,
                status="running_modules",
                started_at=utc_now() - timedelta(seconds=30),
                cancel_requested=False,
                attempt_count=1,
                safety_mode=False,
            )
        )
        session.add(
            WorkflowRunRow(
                id=young_id,
                workflow_id="quick_review",
                transcript_id=tid,
                status="running_modules",
                started_at=utc_now(),
                cancel_requested=False,
                attempt_count=1,
                safety_mode=False,
            )
        )
        session.flush()

    cancelled = workflow_job_service.enforce_kill_mode()
    assert cancelled >= 2
    with get_session() as session:
        assert session.get(WorkflowRunRow, old_id).status == "cancelled"
        assert session.get(WorkflowRunRow, young_id).status == "cancelled"


def test_idle_status_payload_shape() -> None:
    from backend.services.power_service import idle_status_payload

    payload = idle_status_payload()
    assert "should_sleep" in payload
    assert "active_jobs" in payload
    assert payload["kill_long_jobs_enabled"] is True


def test_power_status_public(client: TestClient) -> None:
    r = client.get("/api/v1/ops/power/status")
    assert r.status_code == 200
    assert "state" in r.json() or "should_sleep" in r.json()


def test_lambda_login_html_exchanges_handoff_for_session() -> None:
    """Wake login must POST /handoff (set cookie) — not bounce via ?handoff= into a loop."""
    from pathlib import Path

    source = Path("infra/lambda/power_control/handler.py").read_text(encoding="utf-8")
    start = source.index('LOGIN_HTML = """') + len('LOGIN_HTML = """')
    end = source.index('"""', start)
    html = source[start:end]
    assert "/api/v1/ops/power/handoff" in html
    assert "JSON.stringify({token: handoff})" in html
    assert "searchParams.set('handoff'" not in html
    # Accept verify payload shape (`status`) as well as Dynamo status (`state`).
    assert "s.state || s.status" in html
