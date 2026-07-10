from pydantic import BaseModel, Field

from backend.domain.enums import SourceType


class HealthResponse(BaseModel):
    status: str
    ffmpeg_available: bool
    ollama_available: bool
    whisper_ready: bool
    diarization_ready: bool = False
    cuda_available: bool = False
    whisper_device: str = "cpu"
    diarization_device: str = "cpu"
    whisper_compute_type: str | None = None


class TranscriptSegmentSchema(BaseModel):
    start: float
    end: float
    text: str


class TranscribeResponse(BaseModel):
    transcript: str
    segments: list[TranscriptSegmentSchema]
    language: str | None = None
    duration_seconds: float | None = None
    speaker_count: int = 1
    speaker_labels: list[str] = Field(default_factory=list)
    diarization_applied: bool = False
    diarization_skip_reason: str | None = None
    transcription_mode: str = "overlap"


class OllamaModelsResponse(BaseModel):
    models: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


class PurposeSchema(BaseModel):
    id: str
    name: str
    description: str
    default_model: str | None = None


class PurposesResponse(BaseModel):
    purposes: list[PurposeSchema] = Field(default_factory=list)


class ModuleSchema(BaseModel):
    id: str
    name: str
    version: str
    description: str
    primary_lens: str
    analytical_level: str
    unit_of_analysis: str
    primary_question: str
    confidence_ceiling: str
    output_schema: str
    enabled: bool
    input_type: str
    recommended_companions: list[str] = Field(default_factory=list)


class ModulesResponse(BaseModel):
    modules: list[ModuleSchema] = Field(default_factory=list)


class RunModuleRequest(BaseModel):
    transcript_id: str
    model: str | None = None


class ModuleRunResponse(BaseModel):
    id: str
    module_id: str
    transcript_id: str
    workflow_run_id: str | None = None
    status: str
    model_used: str | None = None
    module_version: str | None = None
    compiler_version: str | None = None
    prompt_template_hash: str | None = None
    raw_output: str | None = None
    parsed_output: dict | None = None
    validation_errors: list[str] | None = None
    safety_flags: list[str] | None = None
    created_at: str
    completed_at: str | None = None


def module_run_to_response(run) -> ModuleRunResponse:
    return ModuleRunResponse(
        id=run.id,
        module_id=run.module_id,
        transcript_id=run.transcript_id,
        workflow_run_id=run.workflow_run_id,
        status=run.status,
        model_used=run.model_used,
        module_version=run.module_version,
        compiler_version=run.compiler_version,
        prompt_template_hash=run.prompt_template_hash,
        raw_output=run.raw_output,
        parsed_output=run.parsed_output,
        validation_errors=run.validation_errors,
        safety_flags=run.safety_flags,
        created_at=run.created_at.isoformat(),
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
    )


class WorkflowSchema(BaseModel):
    id: str
    name: str
    version: str
    description: str
    estimated_runtime: str
    recommended_model: str | None = None
    output_tone: str = ""
    modules: list[str] = Field(default_factory=list)
    meta_synthesis: bool
    enabled: bool


class WorkflowsResponse(BaseModel):
    workflows: list[WorkflowSchema] = Field(default_factory=list)


class RunWorkflowRequest(BaseModel):
    transcript_id: str
    model: str | None = None
    background: bool | None = None


class WorkflowRunModuleSummary(BaseModel):
    id: str
    module_id: str
    status: str
    parsed_output: dict | None = None


class WorkflowRunResponse(BaseModel):
    id: str
    workflow_id: str
    transcript_id: str
    status: str
    model_used: str | None = None
    started_at: str
    completed_at: str | None = None
    error_log: str | None = None
    module_runs: list[WorkflowRunModuleSummary] = Field(default_factory=list)


class SynthesisFindingResponse(BaseModel):
    id: str
    module_run_id: str
    type: str
    title: str
    summary: str
    confidence: str
    evidence_quote_ids: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class SynthesisReportResponse(BaseModel):
    id: str
    workflow_run_id: str
    executive_summary: str
    high_confidence_findings: list[SynthesisFindingResponse] = Field(default_factory=list)
    moderate_confidence_findings: list[SynthesisFindingResponse] = Field(
        default_factory=list
    )
    exploratory_hypotheses: list[SynthesisFindingResponse] = Field(default_factory=list)
    convergence: list[str] = Field(default_factory=list)
    divergence: list[str] = Field(default_factory=list)
    integrated_model: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)
    outstanding_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    source_module_run_ids: list[str] = Field(default_factory=list)
    created_at: str | None = None


def synthesis_report_to_response(report) -> SynthesisReportResponse:
    def finding_rows(findings):
        return [
            SynthesisFindingResponse(
                id=finding.id,
                module_run_id=finding.module_run_id,
                type=finding.type.value,
                title=finding.title,
                summary=finding.summary,
                confidence=finding.confidence.value,
                evidence_quote_ids=finding.evidence_quote_ids,
                alternative_explanations=finding.alternative_explanations,
                limitations=finding.limitations,
            )
            for finding in findings
        ]

    return SynthesisReportResponse(
        id=report.id,
        workflow_run_id=report.workflow_run_id,
        executive_summary=report.executive_summary,
        high_confidence_findings=finding_rows(report.high_confidence_findings),
        moderate_confidence_findings=finding_rows(report.moderate_confidence_findings),
        exploratory_hypotheses=finding_rows(report.exploratory_hypotheses),
        convergence=report.convergence,
        divergence=report.divergence,
        integrated_model=report.integrated_model,
        interventions=report.interventions,
        outstanding_questions=report.outstanding_questions,
        limitations=report.limitations,
        safety_flags=report.safety_flags,
        source_module_run_ids=report.source_module_run_ids,
        created_at=report.created_at.isoformat() if report.created_at else None,
    )


def workflow_run_to_response(
    workflow_run,
    module_runs=None,
) -> WorkflowRunResponse:
    summaries = []
    if module_runs:
        summaries = [
            WorkflowRunModuleSummary(
                id=run.id,
                module_id=run.module_id,
                status=run.status,
                parsed_output=run.parsed_output,
            )
            for run in module_runs
        ]
    return WorkflowRunResponse(
        id=workflow_run.id,
        workflow_id=workflow_run.workflow_id,
        transcript_id=workflow_run.transcript_id,
        status=workflow_run.status,
        model_used=workflow_run.model_used,
        started_at=workflow_run.started_at.isoformat(),
        completed_at=workflow_run.completed_at.isoformat()
        if workflow_run.completed_at
        else None,
        error_log=workflow_run.error_log,
        module_runs=summaries,
    )


class StreamModuleRequest(BaseModel):
    transcript: str
    model: str | None = None


class ProcessResponse(BaseModel):
    transcript: str
    segments: list[TranscriptSegmentSchema]
    language: str | None = None
    duration_seconds: float | None = None
    model: str
    analysis: str
    workflow_id: str | None = None
    workflow_name: str | None = None
    workflow_run_id: str | None = None
    transcript_id: str | None = None


class CreateTranscriptRequest(BaseModel):
    raw_text: str
    source_type: SourceType = SourceType.PASTE
    title: str | None = None
    language: str | None = None


class SpeakerUpdateItem(BaseModel):
    id: str
    label: str | None = None
    display_name: str | None = None


class UpdateSpeakersRequest(BaseModel):
    speakers: list[SpeakerUpdateItem]


class TranscriptResponse(BaseModel):
    id: str
    title: str
    raw_text: str
    source_type: SourceType
    language: str | None = None
    created_at: str


class SpeakerResponse(BaseModel):
    id: str
    transcript_id: str
    label: str
    display_name: str | None = None


class TurnResponse(BaseModel):
    id: str
    transcript_id: str
    speaker_id: str
    turn_index: int
    text: str
    start_time: str | None = None
    end_time: str | None = None


class EvidenceQuoteResponse(BaseModel):
    id: str
    transcript_id: str
    turn_id: str
    speaker_id: str
    quote_index: int
    quote_id: str
    text: str
    context_before: str | None = None
    context_after: str | None = None


class TranscriptBundleResponse(BaseModel):
    transcript: TranscriptResponse
    speakers: list[SpeakerResponse] = Field(default_factory=list)
    turns: list[TurnResponse] = Field(default_factory=list)
    evidence_quotes: list[EvidenceQuoteResponse] = Field(default_factory=list)


class ExplorationFindingSummary(BaseModel):
    finding_key: str
    module_id: str
    module_run_id: str
    id: str | None = None
    type: str | None = None
    title: str | None = None
    summary: str | None = None
    confidence: str | None = None
    evidence_quote_ids: list[str] = Field(default_factory=list)


class ExplorationFindingsResponse(BaseModel):
    workflow_run_id: str
    findings: list[ExplorationFindingSummary] = Field(default_factory=list)


class ExplorationEvidenceQuote(BaseModel):
    quote_id: str
    text: str
    speaker: str
    turn_index: int
    context_before: str | None = None
    context_after: str | None = None


class ExplorationRelatedFinding(BaseModel):
    finding_key: str
    module_id: str
    title: str | None = None
    shared_evidence_quote_ids: list[str] = Field(default_factory=list)


class FindingDrilldownResponse(BaseModel):
    finding_key: str
    finding: dict
    module_id: str
    module_run_id: str
    workflow_run_id: str
    transcript_id: str
    evidence_chain: list[ExplorationEvidenceQuote] = Field(default_factory=list)
    related_findings: list[ExplorationRelatedFinding] = Field(default_factory=list)
    linked_constructs: list[dict] = Field(default_factory=list)


class CrossModuleAlignmentGroup(BaseModel):
    finding_keys: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    shared_evidence_quote_ids: list[str] = Field(default_factory=list)
    shared_title_terms: list[str] = Field(default_factory=list)
    alignment: str
    notes: list[str] = Field(default_factory=list)


class CrossModuleAlignmentResponse(BaseModel):
    workflow_run_id: str
    agreements: list[CrossModuleAlignmentGroup] = Field(default_factory=list)
    disagreements: list[CrossModuleAlignmentGroup] = Field(default_factory=list)
    synthesis: dict | None = None


class KnowledgeGraphNode(BaseModel):
    id: str
    type: str
    label: str
    module_id: str
    confidence: str | None = None
    evidence_quote_ids: list[str] = Field(default_factory=list)


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship_type: str
    module_id: str
    confidence: str | None = None


class KnowledgeGraphResponse(BaseModel):
    workflow_run_id: str
    nodes: list[KnowledgeGraphNode] = Field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = Field(default_factory=list)


class CompareWorkflowRunsRequest(BaseModel):
    workflow_run_ids: list[str] = Field(min_length=2)


class CompareWorkflowRunSummary(BaseModel):
    workflow_run_id: str
    workflow_id: str
    transcript_id: str
    completed_at: str | None = None
    finding_count: int
    findings: list[ExplorationFindingSummary] = Field(default_factory=list)


class CompareWorkflowRunsResponse(BaseModel):
    workflow_run_ids: list[str]
    runs: list[CompareWorkflowRunSummary] = Field(default_factory=list)
    shared_themes: list[dict] = Field(default_factory=list)
    recurring_evidence_quote_ids: list[dict] = Field(default_factory=list)


class AskFollowupRequest(BaseModel):
    question: str
    model: str | None = None
    finding_key: str | None = None


class AskFollowupResponse(BaseModel):
    workflow_run_id: str
    finding_key: str | None = None
    question: str
    answer: str
    model_used: str
    context_scope: str | None = None


class TranscriptWorkflowRunSummary(BaseModel):
    id: str
    workflow_id: str
    transcript_id: str
    status: str
    model_used: str | None = None
    started_at: str
    completed_at: str | None = None


class TranscriptWorkflowRunsResponse(BaseModel):
    transcript_id: str
    workflow_runs: list[TranscriptWorkflowRunSummary] = Field(default_factory=list)


def bundle_to_response(bundle) -> TranscriptBundleResponse:
    transcript = bundle.transcript
    return TranscriptBundleResponse(
        transcript=TranscriptResponse(
            id=transcript.id,
            title=transcript.title,
            raw_text=transcript.raw_text,
            source_type=transcript.source_type,
            language=transcript.language,
            created_at=transcript.created_at.isoformat(),
        ),
        speakers=[
            SpeakerResponse(
                id=speaker.id,
                transcript_id=speaker.transcript_id,
                label=speaker.label,
                display_name=speaker.display_name,
            )
            for speaker in bundle.speakers
        ],
        turns=[
            TurnResponse(
                id=turn.id,
                transcript_id=turn.transcript_id,
                speaker_id=turn.speaker_id,
                turn_index=turn.turn_index,
                text=turn.text,
                start_time=turn.start_time,
                end_time=turn.end_time,
            )
            for turn in bundle.turns
        ],
        evidence_quotes=[
            EvidenceQuoteResponse(
                id=quote.id,
                transcript_id=quote.transcript_id,
                turn_id=quote.turn_id,
                speaker_id=quote.speaker_id,
                quote_index=quote.quote_index,
                quote_id=quote.quote_id,
                text=quote.text,
                context_before=quote.context_before,
                context_after=quote.context_after,
            )
            for quote in bundle.evidence_quotes
        ],
    )
