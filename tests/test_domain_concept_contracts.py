from datetime import datetime

from backend.domain.case import CaseDetail
from backend.domain.concept_contracts import (
    AnalysisScope,
    AnalysisScopeType,
    CaseEvidenceCorpus,
    CompatibilityPosture,
    CorpusPatternAssessment,
    HypothesisSupportAssessment,
    HypothesisSupportLevel,
    ReflectionLens,
    ReflectionPoint,
    ReflectionReport,
    ReflectionRun,
    ReportScope,
    SafetyPosture,
    SafetyPostureLevel,
    ValidationStatus,
    concept_term_for,
    get_domain_term_mapping,
)
from backend.domain.enums import Confidence
from backend.domain.finding import ModuleDefinition
from backend.domain.synthesis import SynthesisReport
from backend.domain.workflow import WorkflowRun


def test_domain_aliases_preserve_existing_runtime_classes() -> None:
    assert ReflectionRun is WorkflowRun
    assert ReflectionLens is ModuleDefinition
    assert ReflectionReport is SynthesisReport
    assert CaseEvidenceCorpus is CaseDetail


def test_legacy_terms_map_to_concept_safe_names() -> None:
    workflow_mapping = get_domain_term_mapping("WorkflowRun")
    assert workflow_mapping is not None
    assert workflow_mapping.concept_term == "ReflectionRun"
    assert workflow_mapping.compatibility_posture == CompatibilityPosture.ALIAS_THEN_MIGRATE

    assert concept_term_for("ModuleDefinition") == "ReflectionLens"
    assert concept_term_for("ModuleRun") == "LensExecution"
    assert concept_term_for("SynthesisReport") == "ReflectionReport"
    assert concept_term_for("safety_mode / safety_flags") == "SafetyPosture"
    assert concept_term_for("unknown") is None


def test_analysis_scope_requires_explicit_version_basis() -> None:
    single = AnalysisScope(
        scope_type=AnalysisScopeType.SINGLE_TRANSCRIPT_VERSION,
        transcript_version_ids=["tv-1"],
    )
    assert single.is_explicit
    assert not single.is_corpus_scope

    missing_version = AnalysisScope(scope_type=AnalysisScopeType.SINGLE_TRANSCRIPT_VERSION)
    assert not missing_version.is_explicit

    corpus = AnalysisScope(
        scope_type=AnalysisScopeType.CASE_EVIDENCE_CORPUS,
        case_id="case-1",
        transcript_version_ids=["tv-1", "tv-2"],
    )
    assert corpus.is_explicit
    assert corpus.is_corpus_scope


def test_hypothesis_support_is_separate_from_confidence() -> None:
    assessment = HypothesisSupportAssessment(
        support_level=HypothesisSupportLevel.PARTIALLY_CONSISTENT,
        confidence=Confidence.LOW,
        evidence_for_quote_ids=["Q001"],
        evidence_against_quote_ids=["Q009"],
        alternative_explanations=["The same behavior could reflect fatigue or context."],
    )

    assert assessment.support_level != assessment.confidence
    assert assessment.has_direct_evidence
    assert assessment.evidence_against_quote_ids == ["Q009"]


def test_safety_posture_identifies_override_levels() -> None:
    calm = SafetyPosture()
    assert calm.posture == SafetyPostureLevel.NONE_DETECTED
    assert not calm.requires_override

    high_risk = SafetyPosture(
        posture=SafetyPostureLevel.HIGH_RISK,
        evidence_quote_ids=["Q007"],
        suppressed_sections=["ordinary_mutual_improvement"],
    )
    assert high_risk.requires_override


def test_reflection_point_is_non_prescriptive_by_default() -> None:
    point = ReflectionPoint(
        id="rp-1",
        title="Pause before responding",
        prompt="What did the evidence suggest you were trying to protect in that moment?",
        evidence_quote_ids=["Q002"],
    )

    assert point.non_prescriptive
    assert point.evidence_quote_ids == ["Q002"]


def test_corpus_pattern_requires_more_than_one_version_for_longitudinal_basis() -> None:
    single_scope = AnalysisScope(
        scope_type=AnalysisScopeType.CASE_EVIDENCE_CORPUS,
        case_id="case-1",
        transcript_version_ids=["tv-1"],
    )
    single_pattern = CorpusPatternAssessment(
        scope=single_scope,
        pattern_name="withdrawal under conflict",
        transcript_version_ids=["tv-1"],
        evidence_quote_ids=["Q001"],
        recurrence_count=1,
    )
    assert not single_pattern.has_longitudinal_basis

    longitudinal_scope = AnalysisScope(
        scope_type=AnalysisScopeType.CASE_EVIDENCE_CORPUS,
        case_id="case-1",
        transcript_version_ids=["tv-1", "tv-2"],
    )
    longitudinal_pattern = CorpusPatternAssessment(
        scope=longitudinal_scope,
        pattern_name="withdrawal under conflict",
        transcript_version_ids=["tv-1", "tv-2"],
        evidence_quote_ids=["Q001", "Q101"],
        recurrence_count=2,
    )
    assert longitudinal_pattern.has_longitudinal_basis


def test_report_scope_keeps_boundary_and_validation_visible() -> None:
    scope = AnalysisScope(
        scope_type=AnalysisScopeType.SINGLE_TRANSCRIPT_VERSION,
        transcript_version_ids=["tv-1"],
    )
    report_scope = ReportScope(
        report_id="report-1",
        analysis_scope=scope,
        reflection_lens_ids=["nvc_reflection"],
        validation_status=ValidationStatus.PASSED_WITH_WARNINGS,
        transcript_is_stale=False,
        export_ready=False,
    )

    assert report_scope.analysis_scope.is_explicit
    assert report_scope.validation_status == ValidationStatus.PASSED_WITH_WARNINGS
    assert "not establish diagnosis" in report_scope.boundary_reminder


def test_reflection_run_alias_can_construct_existing_workflow_run() -> None:
    run = ReflectionRun(
        id="run-1",
        workflow_id="workflow-1",
        transcript_id="transcript-1",
        status="created",
        started_at=datetime.utcnow(),
        transcript_version_id="tv-1",
    )

    assert isinstance(run, WorkflowRun)
    assert run.transcript_version_id == "tv-1"
