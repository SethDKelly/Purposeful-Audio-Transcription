from fastapi import APIRouter
from sqlalchemy import text

from backend.api.schemas import HealthResponse
from backend.core.device import cuda_available
from backend.db.base import engine
from backend.services.audio_service import check_ffmpeg_available
from backend.services.diarization_service import diarization_service
from backend.services.llm_factory import get_llm_provider
from backend.services.ollama_service import ollama_service
from backend.services.transcription_factory import get_transcription_provider
from config.settings import settings

router = APIRouter(prefix="/api", tags=["health"])


def _database_available() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _whisper_ready() -> bool:
    if settings.transcription_provider.strip().lower() not in {"", "whisper"}:
        return False
    try:
        from backend.services.whisper_service import whisper_service

        return whisper_service.is_ready()
    except Exception:
        return False


@router.get("/live")
def live() -> dict[str, str]:
    """Liveness for ALB/ECS — must return immediately with no dependency I/O."""
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    ffmpeg_ok = check_ffmpeg_available()
    llm = get_llm_provider()
    llm_ok = llm.health_check()
    ollama_ok = ollama_service.health_check() if settings.llm_provider == "ollama" else llm_ok
    asr = get_transcription_provider()
    asr_ok = asr.health_check()
    whisper_ok = _whisper_ready() if asr.name == "whisper" else asr_ok
    diarization_ok = (
        diarization_service.is_available()
        if asr.name == "whisper"
        else False
    )
    database_ok = _database_available()

    if settings.llm_provider == "bedrock":
        all_ok = llm_ok and database_ok and asr_ok
    else:
        all_ok = ffmpeg_ok and ollama_ok and whisper_ok and database_ok

    whisper_device = "n/a"
    whisper_compute = None
    diarization_device = "n/a"
    if asr.name == "whisper":
        try:
            from backend.services.whisper_service import whisper_service

            whisper_device = whisper_service.resolved_device()
            whisper_compute = whisper_service.resolved_compute_type()
            diarization_device = diarization_service.resolved_device()
        except Exception:
            whisper_device = "cpu"
            diarization_device = "cpu"

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        ffmpeg_available=ffmpeg_ok,
        ollama_available=ollama_ok,
        llm_provider=settings.llm_provider,
        llm_available=llm_ok,
        database_available=database_ok,
        whisper_ready=whisper_ok,
        diarization_ready=diarization_ok,
        cuda_available=cuda_available(),
        whisper_device=whisper_device,
        diarization_device=diarization_device,
        whisper_compute_type=whisper_compute,
    )
