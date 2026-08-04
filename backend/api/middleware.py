from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from backend.core.log_context import request_id_var
from backend.services.auth_service import auth_service
from config.settings import settings

_PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/health",
    "/api/live",
}


def _is_public(path: str) -> bool:
    if path in _PUBLIC_PATHS or path.startswith("/docs/"):
        return True
    if path.startswith("/api/v1/auth/"):
        return True
    # Power status/handoff must work during wake without a prior session.
    if path in {
        "/api/v1/ops/power/status",
        "/api/v1/ops/power/handoff",
    }:
        return True
    return False


def _is_legacy_admin_api(path: str) -> bool:
    """Legacy ``/api/*`` (non-v1) is Streamlit admin/eval — not multi-user product."""
    if not path.startswith("/api/"):
        return False
    if path.startswith("/api/v1/"):
        return False
    if path in {"/api/health", "/api/live"}:
        return False
    return True


def _unauthorized(request_id: str | None) -> JSONResponse:
    payload: dict[str, object] = {"detail": "Invalid or missing credentials"}
    if request_id:
        payload["request_id"] = request_id
    return JSONResponse(status_code=401, content=payload)


def _forbidden(request_id: str | None) -> JSONResponse:
    payload: dict[str, object] = {"detail": "Admin access required for legacy API routes"}
    if request_id:
        payload["request_id"] = request_id
    return JSONResponse(status_code=403, content=payload)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Gate requests when API key and/or session auth is required.

    - Auth endpoints under ``/api/v1/auth/`` are always public.
    - Valid ``X-API-Key`` (when configured) or session cookie satisfies the gate.
    - When neither auth mode is enabled, all routes pass (local/pytest default).
    - Legacy ``/api/*`` (non-v1) requires admin (API key or session admin) when
      auth is enabled, so ownership cannot be bypassed via Streamlit-era routes.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = request.url.path
        if _is_public(path):
            return await call_next(request)

        api_enabled = settings.api_auth_enabled
        session_required = settings.session_auth_required
        if not api_enabled and not session_required:
            return await call_next(request)

        provided = request.headers.get("X-API-Key")
        api_ok = bool(api_enabled and provided and provided == settings.api_key)

        raw_cookie = request.cookies.get(settings.session_cookie_name)
        session_user = auth_service.resolve_session_token(raw_cookie)
        session_ok = session_user is not None

        if not (api_ok or session_ok):
            request_id = request_id_var.get()
            return _unauthorized(request_id)

        # Non-admin session users must use /api/v1 (ownership-enforced).
        if (
            _is_legacy_admin_api(path)
            and not api_ok
            and not (session_user and session_user.is_admin)
        ):
            return _forbidden(request_id_var.get())

        # Touch idle activity clock for authenticated traffic.
        try:
            from backend.services.power_service import power_state_store

            power_state_store.touch_activity()
        except Exception:  # noqa: BLE001
            pass
        return await call_next(request)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Propagate or generate X-Request-ID for log correlation."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)
