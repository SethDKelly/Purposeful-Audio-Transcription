from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api.middleware import APIKeyMiddleware, RequestContextMiddleware
from backend.api.routes import exploration, health, models, module_stream, modules, process, purposes, transcribe, transcripts, workflows
from backend.core.exceptions import AppError
from backend.core.logging_config import configure_logging
from backend.db.base import init_db
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    workflow_job_service.resume_incomplete()
    yield
    workflow_job_service.shutdown()


configure_logging()

app = FastAPI(
    title="Purposeful Audio Transcription",
    description="Local audio transcription with Whisper and Ollama-powered analysis",
    version="0.3.0",
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
        "database": "postgresql" if not settings.is_sqlite else "sqlite",
    }
