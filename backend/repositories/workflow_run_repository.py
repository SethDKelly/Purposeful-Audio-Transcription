import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import WorkflowRunNotFoundError
from backend.db.models import WorkflowRunRow
from backend.domain.enums import WorkflowRunStatus
from backend.domain.workflow import WorkflowRun


class WorkflowRunRepository:
    def create(
        self,
        session: Session,
        *,
        workflow_id: str,
        transcript_id: str,
        model_used: str | None = None,
    ) -> WorkflowRun:
        now = utc_now()
        run = WorkflowRun(
            id=new_workflow_run_id(),
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            status=WorkflowRunStatus.CREATED.value,
            model_used=model_used,
            started_at=now,
        )
        session.add(_to_row(run))
        session.flush()
        return run

    def save(self, session: Session, run: WorkflowRun) -> WorkflowRun:
        row = session.get(WorkflowRunRow, run.id)
        if row is None:
            session.add(_to_row(run))
        else:
            _update_row(row, run)
        return run

    def get(self, session: Session, run_id: str) -> WorkflowRun:
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            raise WorkflowRunNotFoundError(f"Workflow run not found: {run_id}")
        return _from_row(row)


def new_workflow_run_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


def _to_row(run: WorkflowRun) -> WorkflowRunRow:
    return WorkflowRunRow(
        id=run.id,
        workflow_id=run.workflow_id,
        transcript_id=run.transcript_id,
        status=run.status,
        model_used=run.model_used,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_log=run.error_log,
    )


def _update_row(row: WorkflowRunRow, run: WorkflowRun) -> None:
    row.status = run.status
    row.model_used = run.model_used
    row.completed_at = run.completed_at
    row.error_log = run.error_log


def _from_row(row: WorkflowRunRow) -> WorkflowRun:
    return WorkflowRun(
        id=row.id,
        workflow_id=row.workflow_id,
        transcript_id=row.transcript_id,
        status=row.status,
        model_used=row.model_used,
        started_at=row.started_at,
        completed_at=row.completed_at,
        error_log=row.error_log,
    )
