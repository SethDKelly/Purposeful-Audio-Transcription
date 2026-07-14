from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.api.schemas import PurposesResponse, PurposeSchema
from backend.core.module_registry import module_registry

router = APIRouter(prefix="/api", tags=["purposes"])

_PURPOSES_DEPRECATION_HEADERS = {
    "Deprecation": "true",
    "Link": '</api/modules>; rel="successor-version"',
    "X-Deprecated-Endpoint": "GET /api/purposes is deprecated. Use GET /api/modules instead.",
}


@router.get(
    "/purposes",
    response_model=PurposesResponse,
    deprecated=True,
    summary="List analysis modules (deprecated alias)",
)
def list_purposes() -> JSONResponse:
    purposes = [
        PurposeSchema(
            id=module.config.id,
            name=module.config.name,
            description=module.config.description,
            default_model=module.config.resolved_model_id,
        )
        for module in module_registry.list_modules()
    ]
    return JSONResponse(
        content=PurposesResponse(purposes=purposes).model_dump(),
        headers=_PURPOSES_DEPRECATION_HEADERS,
    )
