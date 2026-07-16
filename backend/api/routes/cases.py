"""Case API routes (v0.9 P1)."""

from datetime import datetime

from fastapi import APIRouter, Response

from backend.api.schemas import (
    AssignTranscriptCaseRequest,
    AssignTranscriptCaseResponse,
    CaseDetailResponse,
    CaseResponse,
    CaseTranscriptSummaryResponse,
    CasesResponse,
    CreateCaseRequest,
    UpdateCaseRequest,
)
from backend.services.case_service import case_service

router = APIRouter(prefix="/api", tags=["cases"])


def _case_response(case) -> CaseResponse:
    return CaseResponse(
        id=case.id,
        title=case.title,
        notes=case.notes,
        created_at=case.created_at.isoformat(),
        updated_at=case.updated_at.isoformat() if case.updated_at else None,
    )


@router.post("/cases", response_model=CaseResponse)
def create_case(request: CreateCaseRequest) -> CaseResponse:
    case = case_service.create(title=request.title, notes=request.notes)
    return _case_response(case)


@router.get("/cases", response_model=CasesResponse)
def list_cases() -> CasesResponse:
    return CasesResponse(cases=[_case_response(case) for case in case_service.list()])


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case(case_id: str) -> CaseDetailResponse:
    detail = case_service.get_detail(case_id)
    return CaseDetailResponse(
        case=_case_response(detail.case),
        transcripts=[
            CaseTranscriptSummaryResponse(
                id=item.id,
                title=item.title,
                session_label=item.session_label,
                session_date=item.session_date.isoformat() if item.session_date else None,
                created_at=item.created_at.isoformat(),
                analysis_ready=item.analysis_ready,
                workflow_run_count=item.workflow_run_count,
            )
            for item in detail.transcripts
        ],
    )


@router.patch("/cases/{case_id}", response_model=CaseResponse)
def update_case(case_id: str, request: UpdateCaseRequest) -> CaseResponse:
    case = case_service.update(case_id, title=request.title, notes=request.notes)
    return _case_response(case)


@router.delete("/cases/{case_id}", status_code=204)
def delete_case(case_id: str) -> Response:
    case_service.delete(case_id)
    return Response(status_code=204)


@router.post("/cases/{case_id}/longitudinal-synthesis")
def run_longitudinal_synthesis(case_id: str, model: str | None = None) -> dict:
    from backend.services.longitudinal_synthesis_service import (
        longitudinal_synthesis_service,
    )

    run = longitudinal_synthesis_service.run(case_id, model=model)
    return {
        "id": run.id,
        "module_id": run.module_id,
        "transcript_id": run.transcript_id,
        "status": run.status,
        "parsed_output": run.parsed_output,
        "validation_errors": run.validation_errors,
        "validation_warnings": run.validation_warnings,
        "model_used": run.model_used,
    }


@router.patch(
    "/transcripts/{transcript_id}/case",
    response_model=AssignTranscriptCaseResponse,
)
def assign_transcript_case(
    transcript_id: str, request: AssignTranscriptCaseRequest
) -> AssignTranscriptCaseResponse:
    session_date = None
    if request.session_date:
        session_date = datetime.fromisoformat(request.session_date.replace("Z", "+00:00"))
        if session_date.tzinfo is not None:
            session_date = session_date.replace(tzinfo=None)
    result = case_service.assign_transcript(
        transcript_id,
        case_id=request.case_id,
        session_label=request.session_label,
        session_date=session_date,
    )
    return AssignTranscriptCaseResponse(**result)
