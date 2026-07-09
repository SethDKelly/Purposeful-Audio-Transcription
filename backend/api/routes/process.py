from fastapi import APIRouter, File, Form, UploadFile

from backend.api.schemas import ProcessResponse, TranscriptSegmentSchema
from backend.core.exceptions import AnalysisError, AudioValidationError
from backend.services.audio_service import saved_upload
from backend.services.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["process"])


@router.post("/process", response_model=ProcessResponse)
async def process(
    file: UploadFile = File(...),
    purpose_id: str | None = Form(None),
    workflow_id: str | None = Form(None),
    model: str | None = Form(None),
) -> ProcessResponse:
    if not file.filename:
        raise AudioValidationError("No filename provided")
    if not workflow_id and not purpose_id:
        raise AnalysisError("Provide workflow_id or purpose_id")

    content = await file.read()
    with saved_upload(content, file.filename) as audio_path:
        if workflow_id:
            result = orchestrator.process_workflow(
                audio_path=audio_path,
                workflow_id=workflow_id,
                model=model,
            )
            return ProcessResponse(
                transcript=result["transcript"],
                segments=[
                    TranscriptSegmentSchema(**segment) for segment in result["segments"]
                ],
                language=result.get("language"),
                duration_seconds=result.get("duration_seconds"),
                model=result["model"],
                analysis=result["analysis"],
                workflow_id=result["workflow_id"],
                workflow_name=result["workflow_name"],
                workflow_run_id=result["workflow_run_id"],
                transcript_id=result["transcript_id"],
            )

        result = orchestrator.process(
            audio_path=audio_path,
            purpose_id=purpose_id,
            model=model,
        )

    return ProcessResponse(
        transcript=result["transcript"],
        segments=[TranscriptSegmentSchema(**segment) for segment in result["segments"]],
        language=result.get("language"),
        duration_seconds=result.get("duration_seconds"),
        model=result["model"],
        analysis=result["analysis"],
        purpose_id=result["purpose_id"],
        purpose_name=result["purpose_name"],
    )
