"""Thin audit ping endpoints (IDs and enums only)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.audit import audit_event

router = APIRouter(prefix="/api", tags=["audit"])

_ALLOWED_EVENTS = frozenset({"transcript.export"})


class AuditEventRequest(BaseModel):
    event: str = Field(..., min_length=1, max_length=128)
    transcript_id: str | None = None
    workflow_run_id: str | None = None
    export_format: str | None = None


@router.post("/audit/events", status_code=204)
def post_audit_event(request: AuditEventRequest) -> None:
    """Record a client-side audit event (e.g. export). Bodies are never accepted."""
    event = request.event.strip()
    if event not in _ALLOWED_EVENTS:
        raise HTTPException(status_code=400, detail=f"Unsupported audit event: {event}")
    audit_event(
        event,
        transcript_id=request.transcript_id,
        workflow_run_id=request.workflow_run_id,
        export_format=request.export_format,
    )
