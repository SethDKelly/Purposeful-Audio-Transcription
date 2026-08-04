"""`/api/v1/ops/power` — idle status, activity, session handoff (when stack is awake)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field

from backend.api.deps import require_admin, require_auth_context
from backend.api.routes.auth import UserMeResponse, _set_session_cookie
from backend.core.exceptions import AuthenticationError
from backend.db.base import get_session
from backend.db.models import UserRow
from backend.services.auth_service import AuthUser
from backend.services.power_service import (
    idle_status_payload,
    parse_handoff_token,
    power_state_store,
)
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/ops/power", tags=["power"])


class HandoffBody(BaseModel):
    token: str = Field(min_length=10, max_length=4000)


@router.get("/status")
def power_status() -> dict:
    return idle_status_payload()


@router.get("/idle-status")
def idle_status(request: Request) -> dict:
    """Called by idle-checker Lambda with API key / admin."""
    require_admin(request)
    return idle_status_payload()


@router.post("/heartbeat")
def heartbeat(request: Request) -> dict[str, str]:
    require_auth_context(request)
    power_state_store.touch_activity()
    return {"status": "ok"}


@router.post("/handoff", response_model=UserMeResponse)
def handoff(body: HandoffBody, request: Request, response: Response) -> UserMeResponse:
    """Exchange Lambda wake handoff token for a Postgres session cookie."""
    from backend.services.power_service import consume_handoff_nonce

    try:
        payload = parse_handoff_token(body.token)
    except ValueError as exc:
        raise AuthenticationError(str(exc)) from exc

    nonce = str(payload.get("nonce") or "").strip()
    if not consume_handoff_nonce(nonce):
        raise AuthenticationError("Handoff token already used or invalid")

    email = str(payload.get("email") or "").strip().lower()
    user_id = str(payload.get("user_id") or "").strip()
    with get_session() as session:
        user = session.scalars(select(UserRow).where(UserRow.email == email)).first()
        if user is None and user_id:
            user = session.get(UserRow, user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Account is not registered")
        auth_user = AuthUser(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_admin=bool(user.is_admin),
        )

    # Create session via verify path internals: request a one-shot session
    from datetime import UTC, datetime, timedelta
    import secrets
    import uuid
    import hashlib
    import json

    from backend.db.models import AuthAuditEventRow, UserSessionRow
    from config.settings import settings

    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    raw_token = secrets.token_urlsafe(32)
    now = datetime.now(UTC).replace(tzinfo=None)
    with get_session() as session:
        session.add(
            UserSessionRow(
                id=str(uuid.uuid4()),
                user_id=auth_user.id,
                session_token_hash=_hash(raw_token),
                created_at=now,
                expires_at=now + timedelta(hours=settings.session_ttl_hours),
                revoked_at=None,
                last_seen_at=now,
                user_agent_hash=None,
                ip_hash=None,
            )
        )
        session.add(
            AuthAuditEventRow(
                id=str(uuid.uuid4()),
                actor_user_id=auth_user.id,
                event_type="auth.handoff",
                resource_type="user",
                resource_id=auth_user.id,
                metadata_json=json.dumps({"email": auth_user.email}),
                created_at=now,
            )
        )
        session.flush()

    _set_session_cookie(response, raw_token)
    power_state_store.touch_activity()
    power_state_store.set_state("awake")
    return UserMeResponse(
        id=auth_user.id,
        email=auth_user.email,
        display_name=auth_user.display_name,
        is_admin=auth_user.is_admin,
    )


@router.post("/start-idle-timer")
def start_idle_timer(request: Request) -> dict[str, str]:
    require_admin(request)
    power_state_store.start_idle_timer()
    return {"status": "ok"}
