"""Case domain model (v0.9)."""

from datetime import datetime

from pydantic import BaseModel, Field


class Case(BaseModel):
    id: str
    title: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class CaseTranscriptSummary(BaseModel):
    id: str
    title: str
    session_label: str | None = None
    session_date: datetime | None = None
    created_at: datetime
    analysis_ready: bool = False
    workflow_run_count: int = 0


class CaseDetail(BaseModel):
    case: Case
    transcripts: list[CaseTranscriptSummary] = Field(default_factory=list)
