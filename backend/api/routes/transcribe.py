import json
from collections.abc import Iterator

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from backend.api.schemas import TranscribeResponse, TranscriptSegmentSchema
from backend.core.exceptions import AudioValidationError, WhisperError
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


@router.post("/transcribe/stream")
async def transcribe_stream(file: UploadFile = File(...)) -> StreamingResponse:
    if not file.filename:
        raise AudioValidationError("No filename provided")

    filename = file.filename
    content = await file.read()

    def event_stream() -> Iterator[bytes]:
        with saved_upload(content, filename) as audio_path:
            try:
                for event in whisper_service.iter_transcription_events(audio_path):
                    yield (json.dumps(event, ensure_ascii=True) + "\n").encode("utf-8")
            except WhisperError as exc:
                payload = {"type": "error", "message": exc.message}
                yield (json.dumps(payload, ensure_ascii=True) + "\n").encode("utf-8")

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
