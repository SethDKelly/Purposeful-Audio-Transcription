from fastapi import APIRouter, File, Form, Response, UploadFile

from backend.api.schemas import (
    CreateTranscriptRequest,
    MarkReadyRequest,
    TranscriptBundleResponse,
    UpdateSpeakersRequest,
    UpdateTurnsRequest,
    bundle_to_response,
)
from backend.core.exceptions import TranscriptValidationError
from backend.domain.enums import SourceType
from backend.domain.transcript import Speaker
from backend.services.transcript_service import transcript_service

router = APIRouter(prefix="/api", tags=["transcripts"])


@router.post("/transcripts", response_model=TranscriptBundleResponse)
def create_transcript(request: CreateTranscriptRequest) -> TranscriptBundleResponse:
    bundle = transcript_service.ingest(
        raw_text=request.raw_text,
        source_type=request.source_type,
        title=request.title,
        language=request.language,
    )
    return bundle_to_response(bundle)


@router.post("/transcripts/upload", response_model=TranscriptBundleResponse)
async def upload_transcript_file(
    file: UploadFile = File(...),
    title: str | None = Form(None),
) -> TranscriptBundleResponse:
    if not file.filename:
        raise TranscriptValidationError("No filename provided")
    if not file.filename.lower().endswith(".txt"):
        raise TranscriptValidationError("Only .txt transcript files are supported")

    content = (await file.read()).decode("utf-8")
    bundle = transcript_service.ingest(
        raw_text=content,
        source_type=SourceType.FILE,
        title=title or file.filename,
    )
    return bundle_to_response(bundle)


@router.get("/transcripts/{transcript_id}", response_model=TranscriptBundleResponse)
def get_transcript(transcript_id: str) -> TranscriptBundleResponse:
    bundle = transcript_service.get(transcript_id)
    return bundle_to_response(bundle)


@router.delete("/transcripts/{transcript_id}", status_code=204)
def delete_transcript(transcript_id: str) -> Response:
    transcript_service.delete(transcript_id)
    return Response(status_code=204)


@router.patch("/transcripts/{transcript_id}/speakers", response_model=TranscriptBundleResponse)
def update_speakers(
    transcript_id: str, request: UpdateSpeakersRequest
) -> TranscriptBundleResponse:
    updates = [
        Speaker(
            id=item.id,
            transcript_id=transcript_id,
            label=item.label or "",
            display_name=item.display_name,
        )
        for item in request.speakers
    ]
    bundle = transcript_service.update_speakers(transcript_id, updates)
    return bundle_to_response(bundle)


@router.patch("/transcripts/{transcript_id}/turns", response_model=TranscriptBundleResponse)
def update_turns(
    transcript_id: str, request: UpdateTurnsRequest
) -> TranscriptBundleResponse:
    patches = [item.model_dump(exclude_unset=True) for item in request.turns]
    bundle = transcript_service.update_turns(transcript_id, patches)
    return bundle_to_response(bundle)


@router.post(
    "/transcripts/{transcript_id}/evidence/rebuild",
    response_model=TranscriptBundleResponse,
)
def rebuild_evidence(transcript_id: str) -> TranscriptBundleResponse:
    bundle = transcript_service.rebuild_evidence_index(transcript_id)
    return bundle_to_response(bundle)


@router.post("/transcripts/{transcript_id}/ready", response_model=TranscriptBundleResponse)
def mark_transcript_ready(
    transcript_id: str, request: MarkReadyRequest | None = None
) -> TranscriptBundleResponse:
    body = request or MarkReadyRequest()
    bundle = transcript_service.mark_ready(
        transcript_id, skip_review=body.skip_review
    )
    return bundle_to_response(bundle)
