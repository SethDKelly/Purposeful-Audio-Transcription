"""Auth dependencies and ownership helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from backend.core.exceptions import AuthenticationError, AuthorizationError
from backend.services.auth_service import AuthUser, auth_service
from config.settings import settings


@dataclass(frozen=True)
class AuthContext:
    user: AuthUser | None
    is_api_key_admin: bool

    @property
    def user_id(self) -> str | None:
        return self.user.id if self.user else None

    @property
    def is_session_admin(self) -> bool:
        return bool(self.user and self.user.is_admin)

    @property
    def is_admin(self) -> bool:
        """API-key break-glass or session admin."""
        return self.is_api_key_admin or self.is_session_admin


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def resolve_auth_context(request: Request) -> AuthContext:
    provided = request.headers.get("X-API-Key")
    is_api_key_admin = bool(
        settings.api_auth_enabled and provided and provided == settings.api_key
    )
    raw = request.cookies.get(settings.session_cookie_name)
    user = auth_service.resolve_session_token(raw)
    return AuthContext(user=user, is_api_key_admin=is_api_key_admin)


def require_auth_context(request: Request) -> AuthContext:
    ctx = resolve_auth_context(request)
    if ctx.user is not None or ctx.is_api_key_admin:
        return ctx
    if settings.session_auth_required or settings.api_auth_enabled:
        raise AuthenticationError("Authentication required")
    return ctx


def require_admin(request: Request) -> AuthContext:
    ctx = require_auth_context(request)
    if not ctx.is_admin:
        raise AuthorizationError("Admin access required")
    return ctx


def assert_resource_owner(owner_user_id: str | None, ctx: AuthContext) -> None:
    """Enforce ownership for session users. Admins bypass. Legacy null owner allowed."""
    if ctx.is_admin:
        return
    if owner_user_id is None:
        return
    if ctx.user is None or ctx.user.id != owner_user_id:
        auth_service.record_audit(
            event_type="auth.ownership_denied",
            actor_user_id=ctx.user_id,
            resource_type="resource",
            resource_id=owner_user_id,
        )
        raise AuthorizationError("Not allowed to access this resource")


def client_ip(request: Request) -> str | None:
    return _client_ip(request)
