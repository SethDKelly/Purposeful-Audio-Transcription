from datetime import datetime

from pydantic import BaseModel, Field

from backend.domain.enums import (
    AnalyticalLevel,
    Confidence,
    FindingType,
    RelationshipType,
)


class Finding(BaseModel):
    id: str
    module_run_id: str
    type: FindingType
    title: str
    summary: str
    confidence: Confidence
    evidence_quote_ids: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    construct_ids: list[str] = Field(default_factory=list)


class Construct(BaseModel):
    id: str
    type: str
    label: str
    description: str | None = None
    confidence: Confidence
    evidence_quote_ids: list[str] = Field(default_factory=list)


class ConstructRelationship(BaseModel):
    id: str
    source_construct_id: str
    target_construct_id: str
    relationship_type: RelationshipType
    confidence: Confidence


class ModuleDefinition(BaseModel):
    id: str
    name: str
    version: str
    primary_lens: str
    analytical_level: AnalyticalLevel
    unit_of_analysis: str
    primary_question: str
    secondary_questions: list[str] = Field(default_factory=list)
    required_constructs: list[str] = Field(default_factory=list)
    output_schema_id: str
    recommended_companions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    inference_depth: str = "medium"
    confidence_ceiling: Confidence = Confidence.MODERATE


class ModuleRun(BaseModel):
    id: str
    module_id: str
    transcript_id: str
    workflow_run_id: str | None = None
    status: str
    model_used: str | None = None
    module_version: str | None = None
    compiler_version: str | None = None
    prompt_template_hash: str | None = None
    prompt_version: str | None = None
    raw_output: str | None = None
    parsed_output: dict | None = None
    validation_errors: list[str] | None = None
    safety_flags: list[str] | None = None
    created_at: datetime
    completed_at: datetime | None = None
