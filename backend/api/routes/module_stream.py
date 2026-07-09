from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api.schemas import StreamModuleRequest
from backend.services.module_runner import module_runner

router = APIRouter(prefix="/api", tags=["modules"])


@router.post("/modules/{module_id}/stream")
def stream_module(module_id: str, request: StreamModuleRequest) -> StreamingResponse:
    def event_generator() -> Iterator[str]:
        yield from module_runner.stream_for_transcript_text(
            module_id=module_id,
            transcript=request.transcript,
            model=request.model,
        )

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")
