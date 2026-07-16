import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import WorkflowRunNotFoundError
from backend.db.models import WorkflowRunRow
from backend.domain.enums import WorkflowRunStatus
from backend.domain.workflow import WorkflowRun

_INCOMPLETE_STATUSES = (
    WorkflowRunStatus.CREATED.value,
    WorkflowRunStatus.PREPROCESSING.value,
    WorkflowRunStatus.RUNNING_MODULES.value,
    WorkflowRunStatus.SYNTHESIZING.value,
)


class WorkflowRunRepository:
    def create(
        self,
        session: Session,
        *,
        workflow_id: str,
        transcript_id: str,
        model_used: str | None = None,
        status: str | None = None,
        safety_mode: bool = False,
    ) -> WorkflowRun:
        now = utc_now()
        run = WorkflowRun(
            id=new_workflow_run_id(),
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            status=status or WorkflowRunStatus.CREATED.value,
            model_used=model_used,
            started_at=now,
            cancel_requested=False,
            attempt_count=0,
            safety_mode=safety_mode,
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

    def list_incomplete(self, session: Session) -> list[WorkflowRun]:
        rows = session.scalars(
            select(WorkflowRunRow).where(WorkflowRunRow.status.in_(_INCOMPLETE_STATUSES))
        ).all()
        return [_from_row(row) for row in rows]

    def list_queued(self, session: Session) -> list[WorkflowRun]:
        """Runs waiting for a worker (CREATED, not cancelled)."""
        rows = session.scalars(
            select(WorkflowRunRow)
            .where(WorkflowRunRow.status == WorkflowRunStatus.CREATED.value)
            .where(WorkflowRunRow.cancel_requested.is_(False))
            .order_by(WorkflowRunRow.started_at.asc())
        ).all()
        return [_from_row(row) for row in rows]

    def claim_queued(self, session: Session, run_id: str) -> WorkflowRun | None:
        """Atomically claim a CREATED run for execution. Returns None if already claimed."""
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            return None
        if row.status != WorkflowRunStatus.CREATED.value or row.cancel_requested:
            return None
        row.status = WorkflowRunStatus.RUNNING_MODULES.value
        row.attempt_count = int(row.attempt_count or 0) + 1
        session.flush()
        return _from_row(row)

    def list_by_transcript_id(
        self,
        session: Session,
        transcript_id: str,
        *,
        status: str | None = None,
    ) -> list[WorkflowRun]:
        query = select(WorkflowRunRow).where(WorkflowRunRow.transcript_id == transcript_id)
        if status is not None:
            query = query.where(WorkflowRunRow.status == status)
        rows = session.scalars(query.order_by(WorkflowRunRow.started_at.desc())).all()
        return [_from_row(row) for row in rows]


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
        telemetry_summary=(
            json.dumps(run.telemetry_summary) if run.telemetry_summary else None
        ),
        cancel_requested=run.cancel_requested,
        attempt_count=run.attempt_count,
        safety_mode=run.safety_mode,
    )


def _update_row(row: WorkflowRunRow, run: WorkflowRun) -> None:
    row.status = run.status
    row.model_used = run.model_used
    row.completed_at = run.completed_at
    row.error_log = run.error_log
    row.telemetry_summary = (
        json.dumps(run.telemetry_summary) if run.telemetry_summary else None
    )
    row.cancel_requested = run.cancel_requested
    row.attempt_count = run.attempt_count
    row.safety_mode = run.safety_mode


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
        telemetry_summary=(
            json.loads(row.telemetry_summary) if row.telemetry_summary else None
        ),
        cancel_requested=bool(row.cancel_requested),
        attempt_count=int(row.attempt_count or 0),
        safety_mode=bool(row.safety_mode),
    )
