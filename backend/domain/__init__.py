"""Domain package exports.

Phase 004-B exposes concept-safe compatibility contracts without renaming the
existing prototype implementation classes or persisted schema fields.
"""

from backend.domain.concept_contracts import (
    AnalysisScope,
    AnalysisScopeType,
    CaseEvidenceCorpus,
    CompatibilityPosture,
    CorpusPatternAssessment,
    DOMAIN_TERMINOLOGY_MAPPINGS,
    DomainTermMapping,
    HypothesisSupportAssessment,
    HypothesisSupportLevel,
    LensExecution,
    PsychologicalHypothesis,
    ReflectionLens,
    ReflectionLensContract,
    ReflectionPoint,
    ReflectionReport,
    ReflectionRun,
    ReportScope,
    SafetyPosture,
    SafetyPostureLevel,
    TRANSCRIPT_AGGREGATE_DECISION,
    ValidationStatus,
    concept_term_for,
    get_domain_term_mapping,
)

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
