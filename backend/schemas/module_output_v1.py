from pydantic import BaseModel, ConfigDict, Field

from backend.domain.enums import Confidence, FindingType, RelationshipType
from backend.domain.finding import Construct, ConstructRelationship, Finding


class FindingInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    module_run_id: str | None = None
    type: FindingType | str
    title: str
    summary: str
    confidence: Confidence | str
    evidence_quote_ids: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    construct_ids: list[str] = Field(default_factory=list)


class ConstructInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    type: str
    label: str
    description: str | None = None
    confidence: Confidence | str
    evidence_quote_ids: list[str] = Field(default_factory=list)


class ConstructRelationshipInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    source_construct_id: str
    target_construct_id: str
    relationship_type: RelationshipType | str
    confidence: Confidence | str


class ModuleRunOutputInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    module_id: str
    module_version: str
    executive_summary: str
    findings: list[FindingInput] = Field(default_factory=list)
    constructs: list[ConstructInput] = Field(default_factory=list)
    relationships: list[ConstructRelationshipInput] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    raw_markdown_report: str = ""


class ModuleRunOutput(BaseModel):
    module_id: str
    module_version: str
    executive_summary: str
    findings: list[Finding] = Field(default_factory=list)
    constructs: list[Construct] = Field(default_factory=list)
    relationships: list[ConstructRelationship] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    raw_markdown_report: str = ""


class SynthesisOutput(BaseModel):
    executive_summary: str
    high_confidence_findings: list[Finding] = Field(default_factory=list)
    moderate_confidence_findings: list[Finding] = Field(default_factory=list)
    exploratory_hypotheses: list[Finding] = Field(default_factory=list)
    convergence: list[str] = Field(default_factory=list)
    divergence: list[str] = Field(default_factory=list)
    integrated_model: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)
    outstanding_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
