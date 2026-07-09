from fastapi import APIRouter, File, Form, UploadFile

from backend.api.schemas import ProcessResponse, TranscriptSegmentSchema
from backend.core.exceptions import AudioValidationError
from backend.services.audio_service import saved_upload
from backend.services.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["process"])


@router.post("/process", response_model=ProcessResponse)
async def process(
    file: UploadFile = File(...),
    purpose_id: str = Form(...),
    model: str | None = Form(None),
) -> ProcessResponse:
    if not file.filename:
        raise AudioValidationError("No filename provided")

    content = await file.read()
    with saved_upload(content, file.filename) as audio_path:
        result = orchestrator.process(
            audio_path=audio_path,
            purpose_id=purpose_id,
            model=model,
        )

    return ProcessResponse(
        transcript=result["transcript"],
        segments=[
            TranscriptSegmentSchema(**segment) for segment in result["segments"]
        ],
        language=result.get("language"),
        duration_seconds=result.get("duration_seconds"),
        purpose_id=result["purpose_id"],
        purpose_name=result["purpose_name"],
        model=result["model"],
        analysis=result["analysis"],
    )
