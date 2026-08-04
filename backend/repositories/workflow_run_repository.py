import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.core.exceptions import WorkflowRunNotFoundError
from backend.db.models import TranscriptRow, TranscriptVersionRow, WorkflowRunRow
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
        owner_user_id: str | None = None,
        transcript_version_id: str | None = None,
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
            transcript_version_id=transcript_version_id,
        )
        session.add(_to_row(run, owner_user_id=owner_user_id))
        session.flush()
        return _enrich_run(session, run)

    def save(self, session: Session, run: WorkflowRun) -> WorkflowRun:
        row = session.get(WorkflowRunRow, run.id)
        if row is None:
            session.add(_to_row(run))
        else:
            _update_row(row, run)
        return _enrich_run(session, run)

    def get(self, session: Session, run_id: str) -> WorkflowRun:
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            raise WorkflowRunNotFoundError(f"Workflow run not found: {run_id}")
        return _enrich_run(session, _from_row(row))

    def list_incomplete(self, session: Session) -> list[WorkflowRun]:
        rows = session.scalars(
            select(WorkflowRunRow).where(WorkflowRunRow.status.in_(_INCOMPLETE_STATUSES))
        ).all()
        return [_enrich_run(session, _from_row(row)) for row in rows]

    def list_queued(self, session: Session) -> list[WorkflowRun]:
        """Runs waiting for a worker (CREATED, not cancelled)."""
        rows = session.scalars(
            select(WorkflowRunRow)
            .where(WorkflowRunRow.status == WorkflowRunStatus.CREATED.value)
            .where(WorkflowRunRow.cancel_requested.is_(False))
            .order_by(WorkflowRunRow.started_at.asc())
        ).all()
        return [_enrich_run(session, _from_row(row)) for row in rows]

    def list_failed(
        self,
        session: Session,
        *,
        limit: int = 50,
    ) -> list[WorkflowRun]:
        rows = session.scalars(
            select(WorkflowRunRow)
            .where(WorkflowRunRow.status == WorkflowRunStatus.FAILED.value)
            .order_by(WorkflowRunRow.completed_at.desc())
            .limit(max(1, min(limit, 200)))
        ).all()
        return [_enrich_run(session, _from_row(row)) for row in rows]

    def queue_stats(self, session: Session) -> dict[str, object]:
        queued = self.list_queued(session)
        now = utc_now()
        oldest_age: float | None = None
        oldest_id: str | None = None
        if queued:
            oldest = queued[0]
            started = oldest.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=UTC)
            oldest_age = max(0.0, (now - started).total_seconds())
            oldest_id = oldest.id
        incomplete = self.list_incomplete(session)
        running = [
            r
            for r in incomplete
            if r.status != WorkflowRunStatus.CREATED.value
        ]
        return {
            "queue_depth": len(queued),
            "oldest_queued_run_id": oldest_id,
            "oldest_queued_age_seconds": oldest_age,
            "running_count": len(running),
            "incomplete_count": len(incomplete),
        }

    def claim_queued(self, session: Session, run_id: str) -> WorkflowRun | None:
        """Atomically claim a CREATED run for execution. Returns None if already claimed.

        Uses a conditional UPDATE so concurrent workers cannot both succeed:
        ``UPDATE … WHERE id=:id AND status='created' AND cancel_requested=false``.
        """
        now = utc_now()
        result = session.execute(
            update(WorkflowRunRow)
            .where(
                WorkflowRunRow.id == run_id,
                WorkflowRunRow.status == WorkflowRunStatus.CREATED.value,
                WorkflowRunRow.cancel_requested.is_(False),
            )
            .values(
                status=WorkflowRunStatus.RUNNING_MODULES.value,
                attempt_count=WorkflowRunRow.attempt_count + 1,
                started_at=now,
            )
        )
        if result.rowcount != 1:
            return None
        # Drop identity map so we reload post-UPDATE values (attempt_count, status).
        session.expire_all()
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            return None
        return _enrich_run(session, _from_row(row))

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
        return [_enrich_run(session, _from_row(row)) for row in rows]


def new_workflow_run_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


def _to_row(run: WorkflowRun, *, owner_user_id: str | None = None) -> WorkflowRunRow:
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
        owner_user_id=owner_user_id,
        transcript_version_id=run.transcript_version_id,
    )


def _update_row(row: WorkflowRunRow, run: WorkflowRun) -> None:
    row.status = run.status
    row.model_used = run.model_used
    row.started_at = run.started_at
    row.completed_at = run.completed_at
    row.error_log = run.error_log
    row.telemetry_summary = (
        json.dumps(run.telemetry_summary) if run.telemetry_summary else None
    )
    row.cancel_requested = run.cancel_requested
    row.attempt_count = run.attempt_count
    row.safety_mode = run.safety_mode
    row.transcript_version_id = run.transcript_version_id


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
        transcript_version_id=getattr(row, "transcript_version_id", None),
    )


def _enrich_run(session: Session, run: WorkflowRun) -> WorkflowRun:
    transcript = session.get(TranscriptRow, run.transcript_id)
    current_version_id = (
        getattr(transcript, "current_version_id", None) if transcript else None
    )
    run.transcript_current_version_id = current_version_id
    version_number = None
    if run.transcript_version_id:
        version = session.get(TranscriptVersionRow, run.transcript_version_id)
        if version is not None:
            version_number = version.version_number
    run.transcript_version_number = version_number
    if run.transcript_version_id and current_version_id:
        run.transcript_is_stale = run.transcript_version_id != current_version_id
    else:
        run.transcript_is_stale = False
    return run
