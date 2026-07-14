from fastapi import APIRouter

from backend.api.schemas import OllamaModelsResponse
from backend.services.llm_factory import get_llm_provider

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models/ollama", response_model=OllamaModelsResponse)
def list_ollama_models() -> OllamaModelsResponse:
    models = get_llm_provider().list_models()
    return OllamaModelsResponse(models=models)
