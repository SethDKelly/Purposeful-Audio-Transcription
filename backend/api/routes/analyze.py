from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api.schemas import AnalyzeRequest, AnalyzeResponse
from backend.core.exceptions import AnalysisError
from backend.services.analysis_service import analysis_service

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    result = analysis_service.analyze(
        transcript=request.transcript,
        purpose_id=request.purpose_id,
        model=request.model,
    )
    return AnalyzeResponse(**result)


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
