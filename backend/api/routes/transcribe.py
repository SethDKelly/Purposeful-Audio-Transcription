from fastapi import APIRouter, File, Form, UploadFile

from backend.api.schemas import TranscribeResponse, TranscriptSegmentSchema
from backend.core.exceptions import AudioValidationError
from backend.services.audio_service import saved_upload
from backend.services.audio_transcription_service import audio_transcription_service

router = APIRouter(prefix="/api", tags=["transcribe"])

MAX_SPEAKER_HINT = 10


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    num_speakers: int | None = Form(None),
) -> TranscribeResponse:
    if not file.filename:
        raise AudioValidationError("No filename provided")

    if num_speakers is not None:
        if num_speakers < 1:
            raise AudioValidationError("num_speakers must be at least 1")
        if num_speakers > MAX_SPEAKER_HINT:
            raise AudioValidationError(f"num_speakers must be at most {MAX_SPEAKER_HINT}")

    content = await file.read()
    with saved_upload(content, file.filename) as audio_path:
        result = audio_transcription_service.transcribe(
            audio_path,
            num_speakers=num_speakers,
        )

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
        speaker_count=result.speaker_count,
        speaker_labels=result.speaker_labels,
        diarization_applied=result.diarization_applied,
        diarization_skip_reason=result.diarization_skip_reason,
    )
