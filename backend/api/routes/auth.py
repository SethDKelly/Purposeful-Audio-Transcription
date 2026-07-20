"""`/api/v1/auth` — passwordless email OTP (phase 003)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field

from backend.api.deps import client_ip, resolve_auth_context
from backend.core.exceptions import AuthenticationError
from backend.services.auth_service import auth_service
from config.settings import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RequestCodeBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class VerifyCodeBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    code: str = Field(min_length=4, max_length=32)


class UserMeResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    is_admin: bool = False


def _set_session_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,  # type: ignore[arg-type]
        max_age=int(settings.session_ttl_hours * 3600),
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )


@router.post("/request-code")
def request_code(body: RequestCodeBody, request: Request) -> dict[str, str]:
    auth_service.request_login_code(body.email, request_ip=client_ip(request))
    return {
        "status": "ok",
        "message": "If the email is valid, a login code was sent.",
    }


@router.post("/verify-code", response_model=UserMeResponse)
def verify_code(
    body: VerifyCodeBody,
    request: Request,
    response: Response,
) -> UserMeResponse:
    user, raw_token = auth_service.verify_login_code(
        body.email,
        body.code,
        request_ip=client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    _set_session_cookie(response, raw_token)
    return UserMeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
    )


@router.post("/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    raw = request.cookies.get(settings.session_cookie_name)
    ctx = resolve_auth_context(request)
    auth_service.logout(raw, actor_user_id=ctx.user_id)
    _clear_session_cookie(response)
    return {"status": "ok"}


@router.get("/me", response_model=UserMeResponse)
def me(request: Request) -> UserMeResponse:
    ctx = resolve_auth_context(request)
    if ctx.user is None:
        raise AuthenticationError("Not signed in")
    return UserMeResponse(
        id=ctx.user.id,
        email=ctx.user.email,
        display_name=ctx.user.display_name,
        is_admin=ctx.user.is_admin,
    )
