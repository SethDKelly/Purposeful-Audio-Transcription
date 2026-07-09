import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import ModuleRunNotFoundError
from backend.db.models import ModuleRunRow
from backend.domain.enums import ModuleRunStatus
from backend.domain.finding import ModuleRun


class ModuleRunRepository:
    def create(
        self,
        session: Session,
        *,
        module_id: str,
        transcript_id: str,
        workflow_run_id: str | None = None,
    ) -> ModuleRun:
        now = utc_now()
        run = ModuleRun(
            id=new_module_run_id(),
            module_id=module_id,
            transcript_id=transcript_id,
            workflow_run_id=workflow_run_id,
            status=ModuleRunStatus.QUEUED.value,
            created_at=now,
        )
        session.add(_to_row(run))
        session.flush()
        return run

    def save(self, session: Session, run: ModuleRun) -> ModuleRun:
        row = session.get(ModuleRunRow, run.id)
        if row is None:
            session.add(_to_row(run))
        else:
            _update_row(row, run)
        return run

    def get(self, session: Session, run_id: str) -> ModuleRun:
        row = session.get(ModuleRunRow, run_id)
        if row is None:
            raise ModuleRunNotFoundError(f"Module run not found: {run_id}")
        return _from_row(row)

    def list_by_workflow_run_id(
        self, session: Session, workflow_run_id: str
    ) -> list[ModuleRun]:
        rows = session.scalars(
            select(ModuleRunRow)
            .where(ModuleRunRow.workflow_run_id == workflow_run_id)
            .order_by(ModuleRunRow.created_at)
        ).all()
        return [_from_row(row) for row in rows]


def new_module_run_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


def _to_row(run: ModuleRun) -> ModuleRunRow:
    return ModuleRunRow(
        id=run.id,
        module_id=run.module_id,
        transcript_id=run.transcript_id,
        workflow_run_id=run.workflow_run_id,
        status=run.status,
        model_used=run.model_used,
        module_version=run.module_version,
        compiler_version=run.compiler_version,
        prompt_template_hash=run.prompt_template_hash,
        raw_output=run.raw_output,
        parsed_output=json.dumps(run.parsed_output) if run.parsed_output else None,
        validation_errors=json.dumps(run.validation_errors) if run.validation_errors else None,
        safety_flags=json.dumps(run.safety_flags) if run.safety_flags else None,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


def _update_row(row: ModuleRunRow, run: ModuleRun) -> None:
    row.status = run.status
    row.model_used = run.model_used
    row.module_version = run.module_version
    row.compiler_version = run.compiler_version
    row.prompt_template_hash = run.prompt_template_hash
    row.raw_output = run.raw_output
    row.parsed_output = json.dumps(run.parsed_output) if run.parsed_output else None
    row.validation_errors = json.dumps(run.validation_errors) if run.validation_errors else None
    row.safety_flags = json.dumps(run.safety_flags) if run.safety_flags else None
    row.completed_at = run.completed_at


def _from_row(row: ModuleRunRow) -> ModuleRun:
    return ModuleRun(
        id=row.id,
        module_id=row.module_id,
        transcript_id=row.transcript_id,
        workflow_run_id=row.workflow_run_id,
        status=row.status,
        model_used=row.model_used,
        module_version=row.module_version,
        compiler_version=row.compiler_version,
        prompt_template_hash=row.prompt_template_hash,
        prompt_version=row.prompt_template_hash,
        raw_output=row.raw_output,
        parsed_output=json.loads(row.parsed_output) if row.parsed_output else None,
        validation_errors=json.loads(row.validation_errors) if row.validation_errors else None,
        safety_flags=json.loads(row.safety_flags) if row.safety_flags else None,
        created_at=row.created_at,
        completed_at=row.completed_at,
    )
