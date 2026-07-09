import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import SynthesisNotFoundError
from backend.db.models import SynthesisReportRow
from backend.domain.synthesis import SynthesisReport


class SynthesisReportRepository:
    def save(self, session: Session, report: SynthesisReport) -> SynthesisReport:
        row = session.get(SynthesisReportRow, report.id)
        payload = report.model_dump(mode="json")
        safety_flags = json.dumps(report.safety_flags) if report.safety_flags else None
        if row is None:
            session.add(
                SynthesisReportRow(
                    id=report.id,
                    workflow_run_id=report.workflow_run_id,
                    report_json=json.dumps(payload),
                    safety_flags=safety_flags,
                    created_at=report.created_at or utc_now(),
                )
            )
        else:
            row.report_json = json.dumps(payload)
            row.safety_flags = safety_flags
        return report

    def get_by_workflow_run_id(
        self, session: Session, workflow_run_id: str
    ) -> SynthesisReport | None:
        row = session.scalars(
            select(SynthesisReportRow).where(
                SynthesisReportRow.workflow_run_id == workflow_run_id
            )
        ).first()
        if row is None:
            return None
        return _from_row(row)

    def get(self, session: Session, report_id: str) -> SynthesisReport:
        row = session.get(SynthesisReportRow, report_id)
        if row is None:
            raise SynthesisNotFoundError(f"Synthesis report not found: {report_id}")
        return _from_row(row)


def new_synthesis_report_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


def _from_row(row: SynthesisReportRow) -> SynthesisReport:
    data = json.loads(row.report_json)
    report = SynthesisReport.model_validate(data)
    if row.safety_flags:
        report.safety_flags = json.loads(row.safety_flags)
    report.created_at = row.created_at
    return report
