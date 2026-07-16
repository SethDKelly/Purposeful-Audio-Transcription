"""Finding feedback API route — use path converter for keys with colons."""

from fastapi import APIRouter

from backend.api.schemas import FindingFeedbackRequest, FindingFeedbackResponse
from backend.db.base import get_session
from backend.repositories.finding_feedback_repository import FindingFeedbackRepository

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post(
    "/workflow-runs/{run_id}/findings/{finding_key:path}/feedback",
    response_model=FindingFeedbackResponse,
)
def submit_finding_feedback(
    run_id: str,
    finding_key: str,
    request: FindingFeedbackRequest,
) -> FindingFeedbackResponse:
    with get_session() as session:
        created = FindingFeedbackRepository().create(
            session,
            finding_key=finding_key,
            rating=request.rating,
            note=request.note,
            workflow_run_id=run_id,
            transcript_id=request.transcript_id,
            case_id=request.case_id,
        )
    return FindingFeedbackResponse(**created)


@router.get(
    "/workflow-runs/{run_id}/feedback",
    response_model=list[FindingFeedbackResponse],
)
def list_workflow_feedback(run_id: str) -> list[FindingFeedbackResponse]:
    with get_session() as session:
        rows = FindingFeedbackRepository().list_for_workflow(session, run_id)
    return [FindingFeedbackResponse(**row) for row in rows]
