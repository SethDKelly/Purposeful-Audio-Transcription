from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.module_output_v1 import FindingInput


class SynthesisOutputInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    executive_summary: str
    high_confidence_findings: list[FindingInput] = Field(default_factory=list)
    moderate_confidence_findings: list[FindingInput] = Field(default_factory=list)
    exploratory_hypotheses: list[FindingInput] = Field(default_factory=list)
    convergence: list[str] = Field(default_factory=list)
    divergence: list[str] = Field(default_factory=list)
    integrated_model: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)
    outstanding_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
