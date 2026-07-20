"""Passwordless email OTP + session auth (phase 003)."""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from backend.core.exceptions import AuthenticationError, AuthValidationError
from backend.db.base import get_session
from backend.db.models import AuthAuditEventRow, LoginCodeRow, UserRow, UserSessionRow
from backend.services.email_delivery import email_delivery
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str
    display_name: str | None
    is_admin: bool


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class AuthService:
    def request_login_code(
        self,
        email: str,
        *,
        request_ip: str | None = None,
    ) -> None:
        normalized = _normalize_email(email)
        if "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise AuthValidationError("Enter a valid email address")

        with get_session() as session:
            hour_ago = _utc_now() - timedelta(hours=1)
            recent = session.scalar(
                select(func.count())
                .select_from(LoginCodeRow)
                .where(LoginCodeRow.email == normalized)
                .where(LoginCodeRow.created_at >= hour_ago)
            )
            if int(recent or 0) >= settings.login_code_rate_limit_per_hour:
                raise AuthValidationError(
                    "Too many login code requests. Try again later."
                )

            code = f"{secrets.randbelow(1_000_000):06d}"
            row = LoginCodeRow(
                id=str(uuid.uuid4()),
                email=normalized,
                code_hash=_hash_secret(code),
                expires_at=_utc_now()
                + timedelta(minutes=settings.login_code_ttl_minutes),
                used_at=None,
                attempt_count=0,
                created_at=_utc_now(),
                request_ip_hash=_hash_secret(request_ip) if request_ip else None,
            )
            session.add(row)
            session.flush()

        email_delivery.send_login_code(email=normalized, code=code)
        logger.info(
            "Login code requested",
            extra={"event": "auth.request_code", "email": normalized},
        )

    def verify_login_code(
        self,
        email: str,
        code: str,
        *,
        request_ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[AuthUser, str]:
        normalized = _normalize_email(email)
        raw_code = (code or "").strip()
        if len(raw_code) < 4:
            raise AuthValidationError("Enter the login code from your email")

        with get_session() as session:
            row = session.scalars(
                select(LoginCodeRow)
                .where(LoginCodeRow.email == normalized)
                .where(LoginCodeRow.used_at.is_(None))
                .order_by(LoginCodeRow.created_at.desc())
            ).first()
            if row is None:
                raise AuthenticationError("Invalid or expired login code")

            if row.expires_at < _utc_now():
                raise AuthenticationError("Login code has expired")

            if int(row.attempt_count or 0) >= settings.login_code_max_attempts:
                raise AuthenticationError("Login code locked after too many attempts")

            if not secrets.compare_digest(row.code_hash, _hash_secret(raw_code)):
                row.attempt_count = int(row.attempt_count or 0) + 1
                session.flush()
                raise AuthenticationError("Invalid or expired login code")

            row.used_at = _utc_now()
            user = session.scalars(
                select(UserRow).where(UserRow.email == normalized)
            ).first()
            if user is None:
                user = UserRow(
                    id=str(uuid.uuid4()),
                    email=normalized,
                    display_name=normalized.split("@")[0],
                    created_at=_utc_now(),
                    last_login_at=_utc_now(),
                    is_active=True,
                    is_admin=False,
                )
                session.add(user)
            else:
                if not user.is_active:
                    raise AuthenticationError("Account is disabled")
                user.last_login_at = _utc_now()

            raw_token = secrets.token_urlsafe(32)
            session_row = UserSessionRow(
                id=str(uuid.uuid4()),
                user_id=user.id,
                session_token_hash=_hash_secret(raw_token),
                created_at=_utc_now(),
                expires_at=_utc_now()
                + timedelta(hours=settings.session_ttl_hours),
                revoked_at=None,
                last_seen_at=_utc_now(),
                user_agent_hash=_hash_secret(user_agent) if user_agent else None,
                ip_hash=_hash_secret(request_ip) if request_ip else None,
            )
            session.add(session_row)
            session.add(
                AuthAuditEventRow(
                    id=str(uuid.uuid4()),
                    actor_user_id=user.id,
                    event_type="auth.login",
                    resource_type="user",
                    resource_id=user.id,
                    metadata_json=json.dumps({"email": normalized}),
                    created_at=_utc_now(),
                )
            )
            session.flush()
            auth_user = AuthUser(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                is_admin=bool(user.is_admin),
            )
            return auth_user, raw_token

    def resolve_session_token(self, raw_token: str | None) -> AuthUser | None:
        if not raw_token:
            return None
        token_hash = _hash_secret(raw_token)
        with get_session() as session:
            row = session.scalars(
                select(UserSessionRow).where(
                    UserSessionRow.session_token_hash == token_hash
                )
            ).first()
            if row is None or row.revoked_at is not None:
                return None
            if row.expires_at < _utc_now():
                return None
            user = session.get(UserRow, row.user_id)
            if user is None or not user.is_active:
                return None
            row.last_seen_at = _utc_now()
            session.flush()
            return AuthUser(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                is_admin=bool(user.is_admin),
            )

    def logout(self, raw_token: str | None, *, actor_user_id: str | None = None) -> None:
        if not raw_token:
            return
        token_hash = _hash_secret(raw_token)
        with get_session() as session:
            row = session.scalars(
                select(UserSessionRow).where(
                    UserSessionRow.session_token_hash == token_hash
                )
            ).first()
            if row is None:
                return
            if row.revoked_at is None:
                row.revoked_at = _utc_now()
                session.add(
                    AuthAuditEventRow(
                        id=str(uuid.uuid4()),
                        actor_user_id=actor_user_id or row.user_id,
                        event_type="auth.logout",
                        resource_type="user_session",
                        resource_id=row.id,
                        metadata_json=None,
                        created_at=_utc_now(),
                    )
                )
                session.flush()

    def record_audit(
        self,
        *,
        event_type: str,
        actor_user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        with get_session() as session:
            session.add(
                AuthAuditEventRow(
                    id=str(uuid.uuid4()),
                    actor_user_id=actor_user_id,
                    event_type=event_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    metadata_json=json.dumps(metadata) if metadata else None,
                    created_at=_utc_now(),
                )
            )
            session.flush()


auth_service = AuthService()
