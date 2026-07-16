from datetime import datetime

from pydantic import BaseModel, Field


class Workflow(BaseModel):
    id: str
    name: str
    version: str
    module_sequence: list[str] = Field(default_factory=list)
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    description: str = ""


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    transcript_id: str
    status: str
    model_used: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    error_log: str | None = None
    telemetry_summary: dict | None = None
    cancel_requested: bool = False
    attempt_count: int = 0
