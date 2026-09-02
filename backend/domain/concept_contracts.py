"""Concept-safe domain compatibility contracts for Phase 004-B.

This module introduces product/concept terminology alongside the existing prototype
implementation names. It intentionally avoids destructive class, table, route, or
API field renames. Existing implementation objects remain valid while later phases
add lifecycle, privacy, analysis, cost-state, UI, and migration gates.
"""

from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel, Field

from backend.domain.case import CaseDetail
from backend.domain.enums import Confidence
from backend.domain.finding import ModuleDefinition, ModuleRun
from backend.domain.synthesis import SynthesisReport
from backend.domain.workflow import WorkflowRun


class CompatibilityPosture(StrEnum):
    """How an accepted concept relates to the current implementation surface."""

    RETAIN = "retain"
    RETAIN_AND_HARDEN = "retain_and_harden"
    ALIAS_THEN_MIGRATE = "alias_then_migrate"
    SPLIT_OR_PROMOTE = "split_or_promote"
    NEW_OR_EQUIVALENT = "new_or_equivalent"
    DEFER = "defer"


class AnalysisScopeType(StrEnum):
    """Explicit evidence scope for retained reflection work."""

    SINGLE_TRANSCRIPT_VERSION = "single_transcript_version"
    SELECTED_TRANSCRIPT_SET = "selected_transcript_set"
    CASE_EVIDENCE_CORPUS = "case_evidence_corpus"
    FUTURE_EXPLICIT_WORKSPACE_CORPUS = "future_explicit_workspace_corpus"


class HypothesisSupportLevel(StrEnum):
    """Relation between evidence and a hypothesis.

    This is intentionally separate from Confidence. Confidence describes evidentiary
    strength; support level describes whether evidence is consistent with a bounded
    hypothesis.
    """

    OBSERVED_BEHAVIOR = "observed_behavior"
    CONSISTENT_WITH_HYPOTHESIS = "consistent_with_hypothesis"
    PARTIALLY_CONSISTENT = "partially_consistent"
    CONTRADICTS = "contradicts"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ALTERNATIVE_EXPLANATION_LIKELY = "alternative_explanation_likely"


class SafetyPostureLevel(StrEnum):
    """Structured safety posture labels for analysis/report behavior."""

    NONE_DETECTED = "none_detected"
    ELEVATED_CAUTION = "elevated_caution"
    HIGH_RISK = "high_risk"
    IMMEDIATE_OR_CRISIS_INDICATORS = "immediate_or_crisis_indicators"


class ValidationStatus(StrEnum):
    """Minimal validation-state vocabulary shared by concept contracts."""

    NOT_EVALUATED = "not_evaluated"
    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    FAILED = "failed"
    BLOCKED = "blocked"


# Runtime aliases preserve current prototype classes while giving later code a stable
# concept-safe import path. These are aliases, not renamed implementations.
ReflectionRun: TypeAlias = WorkflowRun
ReflectionLens: TypeAlias = ModuleDefinition
LensExecution: TypeAlias = ModuleRun
ReflectionReport: TypeAlias = SynthesisReport
CaseEvidenceCorpus: TypeAlias = CaseDetail


class DomainTermMapping(BaseModel):
    """Compatibility map from current code terminology to accepted concept language."""

    legacy_term: str
    concept_term: str
    compatibility_posture: CompatibilityPosture
    user_facing_allowed: bool = False
    notes: str = ""


DOMAIN_TERMINOLOGY_MAPPINGS: tuple[DomainTermMapping, ...] = (
    DomainTermMapping(
        legacy_term="WorkflowRun",
        concept_term="ReflectionRun",
        compatibility_posture=CompatibilityPosture.ALIAS_THEN_MIGRATE,
        notes="WorkflowRun remains internal orchestration; ReflectionRun is product/domain language.",
    ),
    DomainTermMapping(
        legacy_term="ModuleDefinition",
        concept_term="ReflectionLens",
        compatibility_posture=CompatibilityPosture.ALIAS_THEN_MIGRATE,
        notes="Modules remain implementation objects; lens contract metadata should wrap them.",
    ),
    DomainTermMapping(
        legacy_term="ModuleRun",
        concept_term="LensExecution",
        compatibility_posture=CompatibilityPosture.ALIAS_THEN_MIGRATE,
        notes="ModuleRun remains execution storage; LensExecution is concept-facing language.",
    ),
    DomainTermMapping(
        legacy_term="SynthesisReport",
        concept_term="ReflectionReport",
        compatibility_posture=CompatibilityPosture.ALIAS_THEN_MIGRATE,
        notes="SynthesisReport remains current output object; ReflectionReport is product language.",
    ),
    DomainTermMapping(
        legacy_term="FindingType.HYPOTHESIS",
        concept_term="PsychologicalHypothesis / HypothesisSupportAssessment",
        compatibility_posture=CompatibilityPosture.SPLIT_OR_PROMOTE,
        notes="Hypothesis support needs source, support level, contrary evidence, alternatives, and limits.",
    ),
    DomainTermMapping(
        legacy_term="FindingType.INTERVENTION / interventions",
        concept_term="ReflectionPoint",
        compatibility_posture=CompatibilityPosture.SPLIT_OR_PROMOTE,
        notes="Reflection points are evidence-linked, non-prescriptive, and safety-bounded.",
    ),
    DomainTermMapping(
        legacy_term="safety_mode / safety_flags",
        concept_term="SafetyPosture",
        compatibility_posture=CompatibilityPosture.SPLIT_OR_PROMOTE,
        notes="Safety posture should drive report behavior, not only annotate output.",
    ),
    DomainTermMapping(
        legacy_term="CaseDetail",
        concept_term="CaseEvidenceCorpus",
        compatibility_posture=CompatibilityPosture.RETAIN_AND_HARDEN,
        notes="Case is the current foundation for explicit multi-transcript corpus boundaries.",
    ),
    DomainTermMapping(
        legacy_term="SourceType.AUDIO",
        concept_term="Recording source marker",
        compatibility_posture=CompatibilityPosture.RETAIN_AND_HARDEN,
        notes="Audio source type is not a complete recording lifecycle boundary.",
    ),
)


class AnalysisScope(BaseModel):
    """Declared evidence scope before prompt construction or report generation."""

    scope_type: AnalysisScopeType
    transcript_version_ids: list[str] = Field(default_factory=list)
    transcript_ids: list[str] = Field(default_factory=list)
    case_id: str | None = None
    description: str = ""

    @property
    def is_corpus_scope(self) -> bool:
        return self.scope_type == AnalysisScopeType.CASE_EVIDENCE_CORPUS

    @property
    def is_explicit(self) -> bool:
        if self.scope_type == AnalysisScopeType.SINGLE_TRANSCRIPT_VERSION:
            return len(self.transcript_version_ids) == 1
        if self.scope_type == AnalysisScopeType.SELECTED_TRANSCRIPT_SET:
            return bool(self.transcript_version_ids)
        if self.scope_type == AnalysisScopeType.CASE_EVIDENCE_CORPUS:
            return bool(self.case_id and self.transcript_version_ids)
        return bool(self.transcript_version_ids)


class ReflectionLensContract(BaseModel):
    """Concept-facing contract over the current module implementation."""

    lens_id: str
    product_name: str
    implementation_module_id: str
    lens_family: str
    source_frameworks: list[str] = Field(default_factory=list)
    primary_question: str
    secondary_questions: list[str] = Field(default_factory=list)
    inference_depth: str = "medium"
    confidence_ceiling: Confidence = Confidence.MODERATE
    requires_evidence_quotes: bool = True
    supports_corpus_reasoning: bool = False
    supports_hypothesis_support: bool = False
    forbidden_claims: list[str] = Field(
        default_factory=lambda: [
            "diagnosis",
            "confirmed_disorder",
            "clinical_treatment_authority",
            "legal_adjudication",
            "hidden_intent_as_fact",
        ]
    )


class HypothesisSupportAssessment(BaseModel):
    """Bounded assessment of how evidence relates to a hypothesis."""

    support_level: HypothesisSupportLevel
    confidence: Confidence
    evidence_for_quote_ids: list[str] = Field(default_factory=list)
    evidence_against_quote_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @property
    def has_direct_evidence(self) -> bool:
        return bool(self.evidence_for_quote_ids or self.evidence_against_quote_ids)


class PsychologicalHypothesis(BaseModel):
    """Non-diagnostic hypothesis object separated from ordinary findings."""

    hypothesis_name: str
    source: str
    scope: AnalysisScope
    subject_ref: str | None = None
    support: HypothesisSupportAssessment
    non_diagnostic_boundary: str = (
        "This is an evidence-limited reflection hypothesis, not a diagnosis, label, or clinical conclusion."
    )


class SafetyPosture(BaseModel):
    """Structured safety posture for downstream report and UI behavior."""

    posture: SafetyPostureLevel = SafetyPostureLevel.NONE_DETECTED
    matched_categories: list[str] = Field(default_factory=list)
    evidence_quote_ids: list[str] = Field(default_factory=list)
    suppressed_sections: list[str] = Field(default_factory=list)
    required_report_behavior: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @property
    def requires_override(self) -> bool:
        return self.posture in {
            SafetyPostureLevel.HIGH_RISK,
            SafetyPostureLevel.IMMEDIATE_OR_CRISIS_INDICATORS,
        }


class ReflectionPoint(BaseModel):
    """Evidence-linked, non-prescriptive reflection prompt."""

    id: str
    title: str
    prompt: str
    evidence_quote_ids: list[str] = Field(default_factory=list)
    related_finding_ids: list[str] = Field(default_factory=list)
    related_hypothesis_ids: list[str] = Field(default_factory=list)
    safety_posture: SafetyPostureLevel = SafetyPostureLevel.NONE_DETECTED
    non_prescriptive: bool = True
    limitations: list[str] = Field(default_factory=list)


class CorpusPatternAssessment(BaseModel):
    """Multi-transcript pattern claim with explicit corpus and evidence lineage."""

    scope: AnalysisScope
    pattern_name: str
    transcript_version_ids: list[str] = Field(default_factory=list)
    evidence_quote_ids: list[str] = Field(default_factory=list)
    recurrence_count: int = 0
    contradiction_quote_ids: list[str] = Field(default_factory=list)
    temporal_change_notes: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @property
    def has_longitudinal_basis(self) -> bool:
        return len(set(self.transcript_version_ids)) > 1


class ReportScope(BaseModel):
    """Concept-facing report scope header contract."""

    report_id: str
    analysis_scope: AnalysisScope
    reflection_lens_ids: list[str] = Field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.NOT_EVALUATED
    safety_posture: SafetyPosture = Field(default_factory=SafetyPosture)
    transcript_is_stale: bool = False
    export_ready: bool = False
    boundary_reminder: str = (
        "Reflection reports summarize evidence-limited analysis and do not establish diagnosis, legal fault, or hidden intent."
    )


TRANSCRIPT_AGGREGATE_DECISION = (
    "Transcript remains the practical near-term aggregate root; ConversationRecord remains conceptual."
)


def get_domain_term_mapping(legacy_term: str) -> DomainTermMapping | None:
    """Return the accepted concept mapping for a legacy/current implementation term."""

    normalized = legacy_term.strip().lower()
    for mapping in DOMAIN_TERMINOLOGY_MAPPINGS:
        if mapping.legacy_term.lower() == normalized:
            return mapping
    return None


def concept_term_for(legacy_term: str) -> str | None:
    """Return the concept-safe term for a legacy/current implementation term."""

    mapping = get_domain_term_mapping(legacy_term)
    return mapping.concept_term if mapping else None


__all__ = [
    "AnalysisScope",
    "AnalysisScopeType",
    "CaseEvidenceCorpus",
    "CompatibilityPosture",
    "CorpusPatternAssessment",
    "DOMAIN_TERMINOLOGY_MAPPINGS",
    "DomainTermMapping",
    "HypothesisSupportAssessment",
    "HypothesisSupportLevel",
    "LensExecution",
    "PsychologicalHypothesis",
    "ReflectionLens",
    "ReflectionLensContract",
    "ReflectionPoint",
    "ReflectionReport",
    "ReflectionRun",
    "ReportScope",
    "SafetyPosture",
    "SafetyPostureLevel",
    "TRANSCRIPT_AGGREGATE_DECISION",
    "ValidationStatus",
    "concept_term_for",
    "get_domain_term_mapping",
]
