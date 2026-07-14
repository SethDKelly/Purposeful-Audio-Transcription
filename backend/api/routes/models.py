from fastapi import APIRouter

from backend.api.schemas import ModelsResponse
from backend.services.llm_factory import get_llm_provider

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
def list_models() -> ModelsResponse:
    return ModelsResponse(models=get_llm_provider().list_models())


@router.get("/models/ollama", response_model=ModelsResponse, deprecated=True)
def list_ollama_models() -> ModelsResponse:
    """Deprecated alias — use GET /api/models."""
    return list_models()
