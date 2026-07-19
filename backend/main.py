from contextlib import asynccontextmanager
import asyncio
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.api.middleware import APIKeyMiddleware, RequestContextMiddleware
from backend.api.routes import (
    audit,
    cases,
    exploration,
    feedback,
    health,
    models,
    module_stream,
    modules,
    process,
    purposes,
    queue,
    transcribe,
    transcripts,
    v1,
    workflows,
)
from backend.core.exceptions import AppError
from backend.core.log_context import request_id_var
from backend.core.logging_config import configure_logging
from backend.db.base import engine, init_db
from backend.services.transcript_service import transcript_service
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings

logger = logging.getLogger(__name__)

_GENERIC_INTERNAL_ERROR = (
    "An unexpected error occurred. Retry later or contact support with the request ID."
)


def _error_payload(
    detail: str,
    request: Request | None = None,
    *,
    error_code: str = "AppError",
    details: object | None = None,
) -> dict[str, object]:
    # Stable client contract (v1.2): error_code + message + request_id.
    # `detail` retained for backward compatibility with existing Streamlit clients.
    payload: dict[str, object] = {
        "detail": detail,
        "error_code": error_code,
        "message": detail,
        "details": details,
    }
    request_id = None
    if request is not None:
        request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = request_id_var.get()
    if request_id:
        payload["request_id"] = request_id
    return payload

# Postgres advisory lock key so only one uvicorn worker runs migrations / purge.
_STARTUP_LOCK_KEY = 87422014


def _acquire_startup_leader() -> bool:
    """Return True if this process should run one-time startup side effects."""
    if settings.is_sqlite:
        return True
    try:
        with engine.connect() as conn:
            locked = conn.execute(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": _STARTUP_LOCK_KEY},
            ).scalar()
            conn.commit()
            return bool(locked)
    except Exception as exc:  # noqa: BLE001
        # Fail closed: prefer a follower over two leaders racing Alembic.
        logger.warning(
            "Startup leader lock failed (%s); treating this worker as non-leader",
            exc,
        )
        return False


def _release_startup_leader() -> None:
    if settings.is_sqlite:
        return
    try:
        with engine.connect() as conn:
            conn.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": _STARTUP_LOCK_KEY},
            )
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Startup leader unlock failed: %s", exc)


def _wait_for_database(timeout_seconds: float = 90.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:  # noqa: BLE001
            time.sleep(1.0)
    return False


def _run_leader_startup() -> None:
    init_db()
    purged = transcript_service.purge_expired()
    if purged:
        logger.info(
            "Purged %s transcript(s) past retention",
            purged,
            extra={"event": "transcript.purge", "purged_count": purged},
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    leader = _acquire_startup_leader()
    if leader:
        try:
            _run_leader_startup()
        finally:
            # Release before yield so a recycled connection does not pin the lock
            # for the whole process lifetime (and so a failed leader does not block).
            _release_startup_leader()
    else:
        logger.info("Non-leader uvicorn worker; waiting briefly for DB then serving")
        if not _wait_for_database():
            logger.warning(
                "Database not ready for non-leader worker; still serving /api/live"
            )

    # Resume after bind so ALB /api/live is not gated on unfinished job recovery.
    resume_task = None
    if leader:
        resume_task = asyncio.create_task(
            asyncio.to_thread(workflow_job_service.resume_incomplete)
        )

    try:
        yield
    finally:
        if resume_task is not None and not resume_task.done():
            resume_task.cancel()
            try:
                await resume_task
            except asyncio.CancelledError:
                pass
        workflow_job_service.shutdown()


configure_logging()

app = FastAPI(
    title="Relationship Reasoning Engine",
    description="AWS transcript analysis with Bedrock and Amazon Transcribe",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RequestContextMiddleware)

app.include_router(health.router)
app.include_router(queue.router)
app.include_router(models.router)
app.include_router(transcribe.router)
app.include_router(purposes.router)
app.include_router(modules.router)
app.include_router(module_stream.router)
app.include_router(workflows.router)
app.include_router(exploration.router)
app.include_router(process.router)
app.include_router(transcripts.router)
app.include_router(cases.router)
app.include_router(feedback.router)
app.include_router(audit.router)
app.include_router(v1.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    payload = _error_payload(
        exc.message,
        request,
        error_code=getattr(exc, "error_code", None) or type(exc).__name__,
        details=getattr(exc, "details", None),
    )
    response = JSONResponse(status_code=exc.status_code, content=payload)
    request_id = payload.get("request_id")
    if isinstance(request_id, str) and request_id:
        response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None) or request_id_var.get() or "-"
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        extra={
            "event": "request.unhandled_error",
            "error_type": type(exc).__name__,
            "request_id": request_id,
        },
    )
    payload = _error_payload(
        _GENERIC_INTERNAL_ERROR,
        request,
        error_code="InternalError",
    )
    response = JSONResponse(status_code=500, content=payload)
    rid = payload.get("request_id")
    if isinstance(rid, str) and rid:
        response.headers["X-Request-ID"] = rid
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Purposeful Audio Transcription",
        "docs": "/docs",
        "health": "/api/health",
        "live": "/api/live",
        "api_v1": "/api/v1",
        "database": "postgresql" if not settings.is_sqlite else "sqlite",
    }
