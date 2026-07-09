from fastapi import APIRouter

from backend.api.schemas import OllamaModelsResponse
from backend.services.ollama_service import ollama_service

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models/ollama", response_model=OllamaModelsResponse)
def list_ollama_models() -> OllamaModelsResponse:
    models = ollama_service.list_models()
    return OllamaModelsResponse(models=models)
