from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from backend.api.schemas import AnalyzeRequest, AnalyzeResponse
from backend.core.exceptions import AnalysisError
from backend.services.analysis_service import analysis_service

router = APIRouter(prefix="/api", tags=["analyze"])

_ANALYZE_DEPRECATION_HEADERS = {
    "Deprecation": "true",
    "Link": '</api/workflows>; rel="successor-version"',
    "X-Deprecated-Endpoint": (
        "POST /api/analyze is deprecated. Use POST /api/workflows/{workflow_id}/run instead."
    ),
}


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    deprecated=True,
    summary="Run legacy single-purpose analysis (deprecated)",
)
def analyze(request: AnalyzeRequest) -> JSONResponse:
    result = analysis_service.analyze(
        transcript=request.transcript,
        purpose_id=request.purpose_id,
        model=request.model,
    )
    return JSONResponse(
        content=AnalyzeResponse(**result).model_dump(),
        headers=_ANALYZE_DEPRECATION_HEADERS,
    )


@router.post("/analyze/stream")
def analyze_stream(request: AnalyzeRequest) -> StreamingResponse:
    try:
        stream = analysis_service.analyze_stream(
            transcript=request.transcript,
            purpose_id=request.purpose_id,
            model=request.model,
        )
    except AnalysisError as exc:
        raise exc

    def event_generator() -> Iterator[str]:
        try:
            for chunk in stream:
                yield chunk
        except AnalysisError:
            raise

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")
