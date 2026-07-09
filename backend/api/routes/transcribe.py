from fastapi import APIRouter, File, UploadFile

from backend.api.schemas import TranscribeResponse, TranscriptSegmentSchema
from backend.core.exceptions import AudioValidationError
from backend.services.audio_service import saved_upload
from backend.services.whisper_service import whisper_service

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    if not file.filename:
        raise AudioValidationError("No filename provided")

    content = await file.read()
    with saved_upload(content, file.filename) as audio_path:
        result = whisper_service.transcribe(audio_path)

    return TranscribeResponse(
        transcript=result.text,
        segments=[
            TranscriptSegmentSchema(
                start=seg.start,
                end=seg.end,
                text=seg.text,
            )
            for seg in result.segments
        ],
        language=result.language,
        duration_seconds=result.duration_seconds,
    )
