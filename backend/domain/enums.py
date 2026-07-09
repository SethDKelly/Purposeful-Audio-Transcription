from enum import StrEnum


class SourceType(StrEnum):
    PASTE = "paste"
    FILE = "file"
    IMPORT = "import"
    AUDIO = "audio"


class Confidence(StrEnum):
    OBSERVED = "observed"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    EXPLORATORY = "exploratory"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class FindingType(StrEnum):
    OBSERVATION = "observation"
    INTERACTION_CYCLE = "interaction_cycle"
    EMOTION = "emotion"
    NEED = "need"
    VALUE = "value"
    BELIEF = "belief"
    NARRATIVE = "narrative"
    REPAIR_ATTEMPT = "repair_attempt"
    ESCALATION_POINT = "escalation_point"
    COMMUNICATION_BEHAVIOR = "communication_behavior"
    HYPOTHESIS = "hypothesis"
    INTERVENTION = "intervention"
    UNCERTAINTY = "uncertainty"


class AnalyticalLevel(StrEnum):
    OBSERVABLE = "observable"
    INDIVIDUAL = "individual"
    RELATIONAL = "relational"
    INTEGRATIVE = "integrative"
    METHODOLOGICAL = "methodological"


class RelationshipType(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTRIBUTES_TO = "contributes_to"
    ESCALATES = "escalates"
    DEESCALATES = "deescalates"
    PROTECTS = "protects"
    THREATENS = "threatens"
    CO_OCCURS_WITH = "co_occurs_with"
    ALTERNATIVE_TO = "alternative_to"
    INTERVENTION_FOR = "intervention_for"


class ModuleRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class WorkflowRunStatus(StrEnum):
    CREATED = "created"
    PREPROCESSING = "preprocessing"
    RUNNING_MODULES = "running_modules"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


CONFIDENCE_RANK: dict[Confidence, int] = {
    Confidence.INSUFFICIENT_EVIDENCE: 1,
    Confidence.EXPLORATORY: 2,
    Confidence.LOW: 3,
    Confidence.MODERATE: 4,
    Confidence.HIGH: 5,
    Confidence.OBSERVED: 6,
}


TRANSCRIPT_RUNNABLE_MODULES = frozenset(
    {
        "relationship_conversation_analysis",
        "nvc_analysis",
        "systems_analysis",
        "bias_epistemic_quality",
    }
)
