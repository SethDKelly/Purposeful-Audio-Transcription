from fastapi import APIRouter

from backend.api.schemas import (
    AskFollowupRequest,
    AskFollowupResponse,
    CompareWorkflowRunsRequest,
    CompareWorkflowRunsResponse,
    CrossModuleAlignmentResponse,
    ExplorationFindingsResponse,
    FindingDrilldownResponse,
    KnowledgeGraphResponse,
    TranscriptWorkflowRunsResponse,
    TranscriptWorkflowRunSummary,
)
from backend.services.exploration_service import exploration_service

router = APIRouter(prefix="/api", tags=["exploration"])


@router.get(
    "/workflow-runs/{run_id}/exploration/findings",
    response_model=ExplorationFindingsResponse,
)
def list_exploration_findings(run_id: str) -> ExplorationFindingsResponse:
    findings = exploration_service.list_findings(run_id)
    return ExplorationFindingsResponse(workflow_run_id=run_id, findings=findings)


@router.get(
    "/workflow-runs/{run_id}/exploration/findings/{finding_key}",
    response_model=FindingDrilldownResponse,
)
def get_finding_drilldown(run_id: str, finding_key: str) -> FindingDrilldownResponse:
    return FindingDrilldownResponse(**exploration_service.get_finding_drilldown(run_id, finding_key))


@router.get(
    "/workflow-runs/{run_id}/exploration/cross-module",
    response_model=CrossModuleAlignmentResponse,
)
def get_cross_module_alignment(run_id: str) -> CrossModuleAlignmentResponse:
    return CrossModuleAlignmentResponse(**exploration_service.get_cross_module_alignment(run_id))


@router.get(
    "/workflow-runs/{run_id}/exploration/knowledge-graph",
    response_model=KnowledgeGraphResponse,
)
def get_knowledge_graph(run_id: str) -> KnowledgeGraphResponse:
    return KnowledgeGraphResponse(**exploration_service.get_knowledge_graph(run_id))


@router.post(
    "/workflow-runs/{run_id}/exploration/ask",
    response_model=AskFollowupResponse,
)
def ask_followup(run_id: str, request: AskFollowupRequest) -> AskFollowupResponse:
    result = exploration_service.ask_followup(
        run_id,
        request.question,
        model=request.model,
        finding_key=request.finding_key,
    )
    return AskFollowupResponse(**result)


@router.post("/exploration/compare", response_model=CompareWorkflowRunsResponse)
def compare_workflow_runs(request: CompareWorkflowRunsRequest) -> CompareWorkflowRunsResponse:
    return CompareWorkflowRunsResponse(**exploration_service.compare_workflow_runs(request.workflow_run_ids))


@router.get(
    "/transcripts/{transcript_id}/workflow-runs",
    response_model=TranscriptWorkflowRunsResponse,
)
def list_transcript_workflow_runs(transcript_id: str) -> TranscriptWorkflowRunsResponse:
    runs = exploration_service.list_transcript_workflow_runs(transcript_id)
    return TranscriptWorkflowRunsResponse(
        transcript_id=transcript_id,
        workflow_runs=[TranscriptWorkflowRunSummary(**run) for run in runs],
    )
