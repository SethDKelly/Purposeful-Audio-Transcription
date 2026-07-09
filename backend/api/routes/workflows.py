from fastapi import APIRouter

from backend.api.schemas import (
    RunWorkflowRequest,
    SynthesisReportResponse,
    WorkflowRunResponse,
    WorkflowSchema,
    WorkflowsResponse,
    synthesis_report_to_response,
    workflow_run_to_response,
)
from backend.core.workflow_registry import workflow_registry
from backend.services.synthesis_engine import synthesis_engine
from backend.services.workflow_engine import workflow_engine

router = APIRouter(prefix="/api", tags=["workflows"])


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
        )
        for workflow in workflow_registry.list_workflows()
    ]
    return WorkflowsResponse(workflows=workflows)


@router.post("/workflows/{workflow_id}/run", response_model=WorkflowRunResponse)
def run_workflow(workflow_id: str, request: RunWorkflowRequest) -> WorkflowRunResponse:
    workflow_run = workflow_engine.run(
        workflow_id=workflow_id,
        transcript_id=request.transcript_id,
        model=request.model,
    )
    _, module_runs = workflow_engine.get_with_module_runs(workflow_run.id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.get("/workflow-runs/{run_id}", response_model=WorkflowRunResponse)
def get_workflow_run(run_id: str) -> WorkflowRunResponse:
    workflow_run, module_runs = workflow_engine.get_with_module_runs(run_id)
    return workflow_run_to_response(workflow_run, module_runs)


@router.get("/workflow-runs/{run_id}/synthesis", response_model=SynthesisReportResponse)
def get_workflow_synthesis(run_id: str) -> SynthesisReportResponse:
    report = synthesis_engine.get_report(run_id)
    return synthesis_report_to_response(report)
