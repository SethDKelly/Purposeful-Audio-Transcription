from datetime import datetime

from pydantic import BaseModel, Field

from backend.domain.finding import Finding


class SynthesisReport(BaseModel):
    id: str
    workflow_run_id: str
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
    safety_flags: list[str] = Field(default_factory=list)
    source_module_run_ids: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
