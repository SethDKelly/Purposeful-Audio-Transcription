from fastapi import APIRouter

from backend.api.schemas import (
    RunCustomWorkflowRequest,
    RunWorkflowRequest,
    SynthesisReportResponse,
    TranscriptLengthAssessmentResponse,
    TranscriptSafetyAssessmentResponse,
    WorkflowRunResponse,
    WorkflowSchema,
    WorkflowsResponse,
    synthesis_report_to_response,
    workflow_run_to_response,
)
from backend.core.exceptions import WorkflowSyncLimitError
from backend.core.workflow_registry import workflow_registry
from backend.services.custom_workflow_service import custom_workflow_service
from backend.services.synthesis_engine import synthesis_engine
from backend.services.transcript_length_service import transcript_length_service
from backend.services.workflow_engine import workflow_engine
from backend.services.workflow_job_service import workflow_job_service
from backend.services.workflow_safety_service import workflow_safety_service
from config.settings import settings

router = APIRouter(prefix="/api", tags=["workflows"])


def _resolve_background(
    *,
    request_background: bool | None,
    workflow_default_background: bool,
    module_count: int,
) -> bool:
    if request_background is not None:
        use_background = request_background
    elif workflow_default_background:
        use_background = True
    else:
        use_background = settings.workflow_background_default

    limit = settings.workflow_sync_module_limit
    if limit > 0 and module_count > limit and not use_background:
        if request_background is False:
            raise WorkflowSyncLimitError(
                f"Workflow has {module_count} modules; synchronous runs are limited to "
                f"{limit}. Pass background=true or raise WORKFLOW_SYNC_MODULE_LIMIT."
            )
        use_background = True
    return use_background


def _start_workflow_run(
    *,
    workflow_id: str,
    transcript_id: str,
    model: str | None,
    background: bool | None,
    workflow_default_background: bool,
    module_count: int,
    safety_mode: bool,
) -> object:
    use_background = _resolve_background(
        request_background=background,
        workflow_default_background=workflow_default_background,
        module_count=module_count,
    )
    if use_background:
        return workflow_job_service.start_background_run(
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            model=model,
            safety_mode=safety_mode,
        )
    return workflow_engine.run(
        workflow_id=workflow_id,
        transcript_id=transcript_id,
        model=model,
        safety_mode=safety_mode,
    )


@router.get("/workflows", response_model=WorkflowsResponse)
def list_workflows() -> WorkflowsResponse:
    workflows = [
        WorkflowSchema(
            id=workflow.config.id,
            name=workflow.config.name,
            version=workflow.config.version,
            description=workflow.config.description,
            estimated_runtime=workflow.config.estimated_runtime,
            recommended_model=workflow.config.recommended_model,
            output_tone=workflow.config.output_tone,
            modules=workflow.module_sequence,
            meta_synthesis=workflow.config.meta_synthesis,
            enabled=workflow.config.enabled,
            default_background=workflow.config.default_background,
            module_count=len(workflow.module_sequence),
        )
        for workflow in workflow_registry.list_workflows()
    ]
    return WorkflowsResponse(workflows=workflows)


@router.post("/workflows/custom/run", response_model=WorkflowRunResponse)
def run_custom_workflow(request: RunCustomWorkflowRequest) -> WorkflowRunResponse:
    safety_mode = workflow_safety_service.resolve_safety_mode(
        request.transcript_id,
        request_flag=request.safety_mode,
    )
    steps = request.steps or None
    definition, workflow_id = custom_workflow_service.build_definition(
        modules=request.modules,
        name=request.name,
        steps=steps,
        safety_mode=safety_mode,
    )
    workflow_run = _start_workflow_run(
        workflow_id=workflow_id,
        transcript_id=request.transcript_id,
        model=request.model,
        background=request.background,
        workflow_default_background=False,
        module_count=len(definition.module_sequence),
        safety_mode=safety_mode,
    )
    _, module_runs = workflow_engine.get_with_module_runs(workflow_run.id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.post("/workflows/{workflow_id}/run", response_model=WorkflowRunResponse)
def run_workflow(workflow_id: str, request: RunWorkflowRequest) -> WorkflowRunResponse:
    workflow = workflow_registry.get(workflow_id)
    safety_mode = workflow_safety_service.resolve_safety_mode(
        request.transcript_id,
        request_flag=request.safety_mode,
    )
    workflow_run = _start_workflow_run(
        workflow_id=workflow_id,
        transcript_id=request.transcript_id,
        model=request.model,
        background=request.background,
        workflow_default_background=workflow.config.default_background,
        module_count=len(workflow.module_sequence),
        safety_mode=safety_mode,
    )
    _, module_runs = workflow_engine.get_with_module_runs(workflow_run.id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.get("/workflow-runs/{run_id}", response_model=WorkflowRunResponse)
def get_workflow_run(run_id: str) -> WorkflowRunResponse:
    workflow_run, module_runs = workflow_engine.get_with_module_runs(run_id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.post("/workflow-runs/{run_id}/cancel", response_model=WorkflowRunResponse)
def cancel_workflow_run(run_id: str) -> WorkflowRunResponse:
    workflow_run = workflow_engine.request_cancel(run_id)
    _, module_runs = workflow_engine.get_with_module_runs(run_id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.get("/workflow-runs/{run_id}/synthesis", response_model=SynthesisReportResponse)
def get_workflow_synthesis(run_id: str) -> SynthesisReportResponse:
    report = synthesis_engine.get_report(run_id)
    return synthesis_report_to_response(report)


@router.get(
    "/transcripts/{transcript_id}/length-assessment",
    response_model=TranscriptLengthAssessmentResponse,
)
def get_transcript_length_assessment(
    transcript_id: str,
) -> TranscriptLengthAssessmentResponse:
    assessment = transcript_length_service.assess_transcript(transcript_id)
    return TranscriptLengthAssessmentResponse(
        quote_count=assessment.quote_count,
        max_quotes=assessment.max_quotes,
        strategy=assessment.strategy,
        warning=assessment.warning,
        omitted_quotes=assessment.omitted_quotes,
    )


@router.get(
    "/transcripts/{transcript_id}/safety-assessment",
    response_model=TranscriptSafetyAssessmentResponse,
)
def get_transcript_safety_assessment(
    transcript_id: str,
) -> TranscriptSafetyAssessmentResponse:
    scan = workflow_safety_service.scan_transcript(transcript_id)
    return TranscriptSafetyAssessmentResponse(
        risk_level=scan.risk_level,
        matched_categories=scan.matched_categories,
        safety_mode_recommended=scan.safety_mode_recommended,
    )
