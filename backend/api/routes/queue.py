"""Queue operations: depth, failed jobs, stale recovery."""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.api.schemas import (
    QueueStatsResponse,
    WorkflowRunsResponse,
    workflow_run_to_response,
)
from backend.services.workflow_job_service import workflow_job_service

router = APIRouter(prefix="/api", tags=["queue"])


@router.get("/queue/stats", response_model=QueueStatsResponse)
def get_queue_stats() -> QueueStatsResponse:
    stats = workflow_job_service.queue_stats()
    return QueueStatsResponse(**stats)


@router.get("/queue/failed", response_model=WorkflowRunsResponse)
def list_failed_jobs(
    limit: int = Query(default=50, ge=1, le=200),
) -> WorkflowRunsResponse:
    runs = workflow_job_service.list_failed(limit=limit)
    return WorkflowRunsResponse(
        runs=[workflow_run_to_response(run, []) for run in runs]
    )


@router.post("/queue/recover-stale")
def recover_stale_jobs() -> dict[str, int]:
    recovered = workflow_job_service.recover_stale()
    return {"recovered": recovered}
