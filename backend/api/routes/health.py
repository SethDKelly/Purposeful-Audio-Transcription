from fastapi import APIRouter

from backend.api.schemas import HealthResponse
from backend.core.device import cuda_available
from backend.services.audio_service import check_ffmpeg_available
from backend.services.diarization_service import diarization_service
from backend.services.llm_factory import get_llm_provider
from backend.services.ollama_service import ollama_service
from backend.services.whisper_service import whisper_service
from config.settings import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    ffmpeg_ok = check_ffmpeg_available()
    llm = get_llm_provider()
    llm_ok = llm.health_check()
    ollama_ok = ollama_service.health_check() if settings.llm_provider == "ollama" else llm_ok
    whisper_ok = whisper_service.is_ready()
    diarization_ok = diarization_service.is_available()

    if settings.llm_provider == "bedrock":
        all_ok = llm_ok
    else:
        all_ok = ffmpeg_ok and ollama_ok and whisper_ok

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        ffmpeg_available=ffmpeg_ok,
        ollama_available=ollama_ok,
        llm_provider=settings.llm_provider,
        llm_available=llm_ok,
        whisper_ready=whisper_ok,
        diarization_ready=diarization_ok,
        cuda_available=cuda_available(),
        whisper_device=whisper_service.resolved_device(),
        diarization_device=diarization_service.resolved_device(),
        whisper_compute_type=whisper_service.resolved_compute_type(),
    )
