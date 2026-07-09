from fastapi import APIRouter

from backend.api.schemas import PurposesResponse, PurposeSchema
from backend.core.purpose_registry import purpose_registry

router = APIRouter(prefix="/api", tags=["purposes"])


@router.get("/purposes", response_model=PurposesResponse)
def list_purposes() -> PurposesResponse:
    purposes = [
        PurposeSchema(
            id=purpose.id,
            name=purpose.name,
            description=purpose.description,
            default_model=purpose.ollama_model,
        )
        for purpose in purpose_registry.list_purposes()
    ]
    return PurposesResponse(purposes=purposes)
