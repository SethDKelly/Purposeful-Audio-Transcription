from fastapi import APIRouter
from sqlalchemy import text

from backend.api.schemas import HealthResponse
from backend.db.base import engine
from backend.services.llm_factory import get_llm_provider
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


@router.get("/live")
def live() -> dict[str, str]:
    """Liveness for ALB/ECS — must return immediately with no dependency I/O."""
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    llm = get_llm_provider()
    llm_ok = llm.health_check()
    asr = get_transcription_provider()
    asr_ok = asr.health_check()
    database_ok = _database_available()
    all_ok = llm_ok and database_ok and asr_ok

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        llm_provider=settings.llm_provider,
        llm_available=llm_ok,
        transcription_provider=asr.name,
        transcription_available=asr_ok,
        database_available=database_ok,
    )
