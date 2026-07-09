import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config.settings import settings
from backend.core.exceptions import AppError
from backend.api.routes import analyze, health, models, process, purposes, transcribe

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Purposeful Audio Transcription",
    description="Local audio transcription with Whisper and Ollama-powered analysis",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(models.router)
app.include_router(transcribe.router)
app.include_router(purposes.router)
app.include_router(analyze.router)
app.include_router(process.router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Purposeful Audio Transcription",
        "docs": "/docs",
        "health": "/api/health",
    }
