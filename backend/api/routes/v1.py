"""Stable `/api/v1` surface for React / generated clients (v1.2+).

Legacy `/api/*` routes remain for Streamlit admin/eval. Prefer `/api/v1` for product clients.
Responses include ``schema_version: "1"`` on envelope helpers where noted.
"""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from backend.api.routes import cases as cases_routes
from backend.api.routes import exploration as exploration_routes
from backend.api.routes import feedback as feedback_routes
from backend.api.routes import modules as modules_routes
from backend.api.routes import transcripts as transcripts_routes
from backend.api.routes import workflows as workflows_routes
from backend.api.schemas import (
    AssignTranscriptCaseRequest,
    AssignTranscriptCaseResponse,
    CaseDetailResponse,
    CaseResponse,
    CasesResponse,
    CompareCaseTranscriptsRequest,
    CompareCaseTranscriptsResponse,
    CreateCaseRequest,
    CreateTranscriptRequest,
    ExplorationFindingsResponse,
    FindingDrilldownResponse,
    FindingFeedbackRequest,
    FindingFeedbackResponse,
    KnowledgeGraphResponse,
    MarkReadyRequest,
    ModulesResponse,
    RunWorkflowRequest,
    StructuredGraphResponse,
    SynthesisReportResponse,
    TranscriptBundleResponse,
    TranscriptSafetyAssessmentResponse,
    TranscriptWorkflowRunsResponse,
    UpdateCaseRequest,
    UpdateSpeakersRequest,
    UpdateTurnsRequest,
    WorkflowRunResponse,
    WorkflowsResponse,
    synthesis_report_to_response,
)
from backend.core.module_registry import module_registry
from backend.db.base import get_session
from backend.repositories.finding_feedback_repository import FindingFeedbackRepository
from backend.services.evaluation_run_service import evaluation_run_service
from backend.services.report_package_service import build_v1_report_package_zip
from backend.services.structured_graph_service import structured_graph_service
from backend.services.synthesis_engine import synthesis_engine
from backend.services.transcript_service import transcript_service
from backend.services.workflow_engine import workflow_engine
from backend.services.workflow_safety_service import workflow_safety_service

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
    redact: bool = False


class ExportV1Response(V1Envelope):
    workflow_run_id: str
    format: str
    download_hint: str


class OfflineEvalRequest(BaseModel):
    fixture_id: str
    module_id: str
    module_output: dict


class ModuleLifecycleItem(BaseModel):
    id: str
    name: str
    version: str
    enabled: bool
    description: str = ""
    output_schema: str = "module_output_v1"
    prompt_file: str = ""
    prompt_sha256: str = ""
    deprecated: bool = False


class ModuleLifecycleResponse(V1Envelope):
    modules: list[ModuleLifecycleItem] = Field(default_factory=list)
    compatibility_note: str = (
        "Reports store module_id + module version at run time; interpret old "
        "outputs with the run's recorded version, not the live registry alone."
    )


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


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case(case_id: str) -> CaseDetailResponse:
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


@router.post("/exports", response_model=None)
def create_export(request: ExportV1Request):
    run = workflow_engine.get(request.workflow_run_id)
    if request.format in {"package", "zip"}:
        report = synthesis_engine.get_report(request.workflow_run_id)
        payload = synthesis_report_to_response(report).model_dump()
        bundle = transcript_service.get(run.transcript_id)
        speakers = {s.id: (s.display_name or s.label) for s in bundle.speakers}
        structured = structured_graph_service.inventory(request.workflow_run_id)
        lifecycle = [
            {
                "id": m.config.id,
                "version": m.config.version,
                "prompt_sha256": hashlib.sha256(m.module_prompt.encode("utf-8")).hexdigest(),
            }
            for m in module_registry.list_modules()
        ]
        zip_bytes = build_v1_report_package_zip(
            workflow_run={
                "id": run.id,
                "workflow_id": run.workflow_id,
                "transcript_id": run.transcript_id,
                "safety_mode": bool(getattr(run, "safety_mode", False)),
            },
            synthesis=payload,
            evidence_quotes=[
                {
                    "quote_id": q.quote_id,
                    "text": q.text,
                    "speaker_label": speakers.get(q.speaker_id, q.speaker_id),
                }
                for q in bundle.evidence_quotes
            ],
            structured=structured,
            module_lifecycle=lifecycle,
            redact=request.redact,
        )
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="rre-report-package-{request.workflow_run_id}.zip"'
                )
            },
        )
    return ExportV1Response(
        workflow_run_id=request.workflow_run_id,
        format=request.format,
        download_hint=f"/api/v1/reports/{request.workflow_run_id}",
    )


@router.get("/workflows", response_model=WorkflowsResponse)
def list_workflows() -> WorkflowsResponse:
    return workflows_routes.list_workflows()


@router.patch("/transcripts/{transcript_id}/speakers", response_model=TranscriptBundleResponse)
def update_speakers(
    transcript_id: str, request: UpdateSpeakersRequest
) -> TranscriptBundleResponse:
    return transcripts_routes.update_speakers(transcript_id, request)


@router.post("/transcripts/{transcript_id}/ready", response_model=TranscriptBundleResponse)
def mark_ready(
    transcript_id: str, request: MarkReadyRequest | None = None
) -> TranscriptBundleResponse:
    return transcripts_routes.mark_transcript_ready(transcript_id, request)


@router.post(
    "/transcripts/{transcript_id}/evidence/rebuild",
    response_model=TranscriptBundleResponse,
)
def rebuild_evidence(transcript_id: str) -> TranscriptBundleResponse:
    return transcripts_routes.rebuild_evidence(transcript_id)


@router.post("/cases", response_model=CaseResponse)
def create_case(request: CreateCaseRequest) -> CaseResponse:
    return cases_routes.create_case(request)


@router.get("/cases", response_model=CasesResponse)
def list_cases() -> CasesResponse:
    return cases_routes.list_cases()


@router.patch("/cases/{case_id}", response_model=CaseResponse)
def update_case(case_id: str, request: UpdateCaseRequest) -> CaseResponse:
    return cases_routes.update_case(case_id, request)


@router.patch(
    "/transcripts/{transcript_id}/case",
    response_model=AssignTranscriptCaseResponse,
)
def assign_transcript_case(
    transcript_id: str, request: AssignTranscriptCaseRequest
) -> AssignTranscriptCaseResponse:
    return cases_routes.assign_transcript_case(transcript_id, request)


@router.delete("/cases/{case_id}", status_code=204)
def delete_case(case_id: str) -> Response:
    return cases_routes.delete_case(case_id)


@router.post("/cases/{case_id}/longitudinal-synthesis")
def run_longitudinal_synthesis(case_id: str, model: str | None = None) -> dict:
    payload = cases_routes.run_longitudinal_synthesis(case_id, model=model)
    return {"schema_version": SCHEMA_VERSION, **payload}


@router.get("/modules", response_model=ModulesResponse)
def list_modules() -> ModulesResponse:
    return modules_routes.list_modules()


@router.get("/modules/lifecycle", response_model=ModuleLifecycleResponse)
def module_lifecycle() -> ModuleLifecycleResponse:
    items: list[ModuleLifecycleItem] = []
    for module in module_registry.list_modules():
        cfg = module.config
        prompt_sha = hashlib.sha256(module.module_prompt.encode("utf-8")).hexdigest()
        items.append(
            ModuleLifecycleItem(
                id=cfg.id,
                name=cfg.name,
                version=cfg.version,
                enabled=cfg.enabled,
                description=cfg.description,
                output_schema=cfg.output_schema,
                prompt_file=cfg.prompt_file,
                prompt_sha256=prompt_sha,
                deprecated=not cfg.enabled,
            )
        )
    return ModuleLifecycleResponse(modules=items)


@router.get(
    "/workflow-runs/{run_id}/knowledge-graph",
    response_model=KnowledgeGraphResponse,
)
def get_knowledge_graph(run_id: str) -> KnowledgeGraphResponse:
    return exploration_routes.get_knowledge_graph(run_id)


@router.get(
    "/workflow-runs/{run_id}/structured-graph",
    response_model=StructuredGraphResponse,
)
def get_structured_graph(run_id: str) -> StructuredGraphResponse:
    return exploration_routes.get_structured_graph(run_id)


@router.post(
    "/exploration/compare-transcripts",
    response_model=CompareCaseTranscriptsResponse,
)
def compare_case_transcripts(
    request: CompareCaseTranscriptsRequest,
) -> CompareCaseTranscriptsResponse:
    return exploration_routes.compare_case_transcripts(request)


@router.get(
    "/transcripts/{transcript_id}/workflow-runs",
    response_model=TranscriptWorkflowRunsResponse,
)
def list_transcript_workflow_runs(transcript_id: str) -> TranscriptWorkflowRunsResponse:
    return exploration_routes.list_transcript_workflow_runs(transcript_id)


@router.get(
    "/transcripts/{transcript_id}/safety-assessment",
    response_model=TranscriptSafetyAssessmentResponse,
)
def get_transcript_safety_assessment(
    transcript_id: str,
) -> TranscriptSafetyAssessmentResponse:
    return workflows_routes.get_transcript_safety_assessment(transcript_id)


@router.get("/transcripts/{transcript_id}/safety-events")
def list_transcript_safety_events(transcript_id: str) -> dict:
    events = workflow_safety_service.list_events(transcript_id=transcript_id)
    return {"schema_version": SCHEMA_VERSION, "transcript_id": transcript_id, "events": events}


@router.get("/workflow-runs/{run_id}/safety-events")
def list_run_safety_events(run_id: str) -> dict:
    events = workflow_safety_service.list_events(workflow_run_id=run_id)
    return {"schema_version": SCHEMA_VERSION, "workflow_run_id": run_id, "events": events}


@router.get(
    "/workflow-runs/{run_id}/findings",
    response_model=ExplorationFindingsResponse,
)
def list_run_findings(run_id: str) -> ExplorationFindingsResponse:
    return exploration_routes.list_exploration_findings(run_id)


@router.get(
    "/workflow-runs/{run_id}/findings/{finding_key:path}",
    response_model=FindingDrilldownResponse,
)
def get_finding_drilldown(run_id: str, finding_key: str) -> FindingDrilldownResponse:
    return exploration_routes.get_finding_drilldown(run_id, finding_key)


@router.get("/evaluations")
def list_evaluations(limit: int = 50) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "runs": evaluation_run_service.list_recent(limit=limit),
    }


@router.get("/evaluations/{run_id}")
def get_evaluation(run_id: str) -> dict:
    from fastapi import HTTPException

    row = evaluation_run_service.get(run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return {"schema_version": SCHEMA_VERSION, **row}


@router.post("/evaluations/runs")
def create_evaluation_run(request: OfflineEvalRequest) -> dict:
    row = evaluation_run_service.run_offline_fixture(
        fixture_id=request.fixture_id,
        module_id=request.module_id,
        module_output=request.module_output,
    )
    return {"schema_version": SCHEMA_VERSION, **row}


@router.get("/cases/{case_id}/pinned-findings")
def list_case_pinned_findings(case_id: str) -> dict:
    detail = cases_routes.get_case(case_id)
    transcript_ids = {t.id for t in detail.transcripts}
    pinned: list[dict] = []
    with get_session() as session:
        for tid in transcript_ids:
            # Collect feedback via workflow runs on each transcript
            runs = exploration_routes.list_transcript_workflow_runs(tid)
            for run in runs.workflow_runs:
                rows = FindingFeedbackRepository().list_for_workflow(session, run.id)
                for row in rows:
                    if row.get("rating") == "pinned":
                        pinned.append({**row, "transcript_id": tid})
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "pinned_findings": pinned,
    }
