"""Stable `/api/v1` surface for React / generated clients (v1.2).

Legacy `/api/*` routes remain for Streamlit. Prefer `/api/v1` for new clients.
Responses include ``schema_version: "1"`` on envelope helpers where noted.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.routes import cases as cases_routes
from backend.api.routes import feedback as feedback_routes
from backend.api.routes import transcripts as transcripts_routes
from backend.api.routes import workflows as workflows_routes
from backend.api.schemas import (
    CreateTranscriptRequest,
    FindingFeedbackRequest,
    FindingFeedbackResponse,
    RunWorkflowRequest,
    SynthesisReportResponse,
    TranscriptBundleResponse,
    UpdateTurnsRequest,
    WorkflowRunResponse,
    synthesis_report_to_response,
)
from backend.services.synthesis_engine import synthesis_engine
from backend.services.workflow_engine import workflow_engine

router = APIRouter(prefix="/api/v1", tags=["v1"])

SCHEMA_VERSION = "1"


class V1Envelope(BaseModel):
    schema_version: str = SCHEMA_VERSION


class StartWorkflowV1Request(RunWorkflowRequest):
    workflow_id: str = "quick_review"


class WorkflowStatusV1Response(V1Envelope):
    id: str
    status: str
    cancel_requested: bool = False
    attempt_count: int = 0
    error_log: str | None = None


class ReportFindingsV1Response(V1Envelope):
    report_id: str
    workflow_run_id: str
    findings: list[dict] = Field(default_factory=list)


class ReportEvidenceV1Response(V1Envelope):
    report_id: str
    workflow_run_id: str
    evidence_quote_ids: list[str] = Field(default_factory=list)


class ExportV1Request(BaseModel):
    workflow_run_id: str
    format: str = "json"


class ExportV1Response(V1Envelope):
    workflow_run_id: str
    format: str
    download_hint: str


@router.post("/transcripts", response_model=TranscriptBundleResponse)
def create_transcript(request: CreateTranscriptRequest) -> TranscriptBundleResponse:
    return transcripts_routes.create_transcript(request)


@router.get("/transcripts/{transcript_id}", response_model=TranscriptBundleResponse)
def get_transcript(transcript_id: str) -> TranscriptBundleResponse:
    return transcripts_routes.get_transcript(transcript_id)


@router.patch("/transcripts/{transcript_id}/turns", response_model=TranscriptBundleResponse)
def update_turns(transcript_id: str, request: UpdateTurnsRequest) -> TranscriptBundleResponse:
    return transcripts_routes.update_turns(transcript_id, request)


@router.post("/workflow-runs", response_model=WorkflowRunResponse)
def start_workflow_run(request: StartWorkflowV1Request) -> WorkflowRunResponse:
    return workflows_routes.run_workflow(
        request.workflow_id,
        RunWorkflowRequest(
            transcript_id=request.transcript_id,
            model=request.model,
            background=request.background,
            safety_mode=request.safety_mode,
        ),
    )


@router.get("/workflow-runs/{run_id}", response_model=WorkflowRunResponse)
def get_workflow_run(run_id: str) -> WorkflowRunResponse:
    return workflows_routes.get_workflow_run(run_id)


@router.get("/workflow-runs/{run_id}/status", response_model=WorkflowStatusV1Response)
def get_workflow_run_status(run_id: str) -> WorkflowStatusV1Response:
    run = workflow_engine.get(run_id)
    return WorkflowStatusV1Response(
        id=run.id,
        status=run.status,
        cancel_requested=run.cancel_requested,
        attempt_count=run.attempt_count,
        error_log=run.error_log,
    )


@router.get("/reports/{run_id}", response_model=SynthesisReportResponse)
def get_report(run_id: str) -> SynthesisReportResponse:
    return workflows_routes.get_workflow_synthesis(run_id)


@router.get("/reports/{run_id}/findings", response_model=ReportFindingsV1Response)
def get_report_findings(run_id: str) -> ReportFindingsV1Response:
    report = synthesis_engine.get_report(run_id)
    payload = synthesis_report_to_response(report)
    findings = [
        f.model_dump()
        for f in (
            payload.high_confidence_findings
            + payload.moderate_confidence_findings
            + payload.exploratory_hypotheses
        )
    ]
    return ReportFindingsV1Response(
        report_id=payload.id,
        workflow_run_id=payload.workflow_run_id,
        findings=findings,
    )


@router.get("/reports/{run_id}/evidence", response_model=ReportEvidenceV1Response)
def get_report_evidence(run_id: str) -> ReportEvidenceV1Response:
    report = synthesis_engine.get_report(run_id)
    quote_ids: list[str] = []
    for finding in (
        report.high_confidence_findings
        + report.moderate_confidence_findings
        + report.exploratory_hypotheses
    ):
        quote_ids.extend(finding.evidence_quote_ids or [])
    # Preserve order, unique
    seen: set[str] = set()
    ordered: list[str] = []
    for qid in quote_ids:
        if qid not in seen:
            seen.add(qid)
            ordered.append(qid)
    return ReportEvidenceV1Response(
        report_id=report.id,
        workflow_run_id=report.workflow_run_id,
        evidence_quote_ids=ordered,
    )


@router.post(
    "/findings/{finding_key:path}/feedback",
    response_model=FindingFeedbackResponse,
)
def submit_finding_feedback_v1(
    finding_key: str,
    request: FindingFeedbackRequest,
    workflow_run_id: str,
) -> FindingFeedbackResponse:
    return feedback_routes.submit_finding_feedback(workflow_run_id, finding_key, request)


@router.get("/cases/{case_id}")
def get_case(case_id: str):
    return cases_routes.get_case(case_id)


@router.get("/cases/{case_id}/timeline")
def get_case_timeline(case_id: str) -> dict:
    detail = cases_routes.get_case(case_id)
    events = [
        {
            "transcript_id": t.id,
            "title": t.title,
            "session_label": t.session_label,
            "session_date": t.session_date,
            "created_at": t.created_at,
            "analysis_ready": t.analysis_ready,
            "workflow_run_count": t.workflow_run_count,
        }
        for t in detail.transcripts
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "events": events,
    }


@router.post("/exports", response_model=ExportV1Response)
def create_export(request: ExportV1Request) -> ExportV1Response:
    # Client-side export remains primary; this endpoint documents the stable contract.
    _ = workflow_engine.get(request.workflow_run_id)
    return ExportV1Response(
        workflow_run_id=request.workflow_run_id,
        format=request.format,
        download_hint=f"/api/workflow-runs/{request.workflow_run_id}/synthesis",
    )
