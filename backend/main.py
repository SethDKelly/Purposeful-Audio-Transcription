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
    exploration,
    health,
    models,
    module_stream,
    modules,
    process,
    purposes,
    transcribe,
    transcripts,
    workflows,
)
from backend.core.exceptions import AppError
from backend.core.logging_config import configure_logging
from backend.db.base import engine, init_db
from backend.services.transcript_service import transcript_service
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings

logger = logging.getLogger(__name__)

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
    version="0.5.1",
    lifespan=lifespan,
)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RequestContextMiddleware)

app.include_router(health.router)
app.include_router(models.router)
app.include_router(transcribe.router)
app.include_router(purposes.router)
app.include_router(modules.router)
app.include_router(module_stream.router)
app.include_router(workflows.router)
app.include_router(exploration.router)
app.include_router(process.router)
app.include_router(transcripts.router)
app.include_router(audit.router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        extra={
            "event": "request.unhandled_error",
            "error_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Purposeful Audio Transcription",
        "docs": "/docs",
        "health": "/api/health",
        "live": "/api/live",
        "database": "postgresql" if not settings.is_sqlite else "sqlite",
    }
