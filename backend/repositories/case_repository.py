"""Case persistence (v0.9 P1)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.exceptions import CaseNotFoundError
from backend.db.models import CaseRow, TranscriptRow, WorkflowRunRow
from backend.domain.case import Case, CaseDetail, CaseTranscriptSummary


class CaseRepository:
    def create(
        self,
        session: Session,
        *,
        title: str,
        notes: str | None = None,
    ) -> Case:
        now = datetime.now(UTC).replace(tzinfo=None)
        case = Case(
            id=str(uuid.uuid4()),
            title=title.strip() or "Untitled case",
            notes=notes,
            created_at=now,
            updated_at=now,
        )
        session.add(
            CaseRow(
                id=case.id,
                title=case.title,
                notes=case.notes,
                created_at=case.created_at,
                updated_at=case.updated_at,
            )
        )
        session.flush()
        return case

    def get(self, session: Session, case_id: str) -> Case:
        row = session.get(CaseRow, case_id)
        if row is None:
            raise CaseNotFoundError(f"Case not found: {case_id}")
        return _from_row(row)

    def list(self, session: Session) -> list[Case]:
        rows = session.scalars(select(CaseRow).order_by(CaseRow.created_at.desc())).all()
        return [_from_row(row) for row in rows]

    def update(
        self,
        session: Session,
        case_id: str,
        *,
        title: str | None = None,
        notes: str | None = None,
    ) -> Case:
        row = session.get(CaseRow, case_id)
        if row is None:
            raise CaseNotFoundError(f"Case not found: {case_id}")
        if title is not None:
            row.title = title.strip() or row.title
        if notes is not None:
            row.notes = notes
        row.updated_at = datetime.now(UTC).replace(tzinfo=None)
        session.flush()
        return _from_row(row)

    def delete(self, session: Session, case_id: str) -> None:
        row = session.get(CaseRow, case_id)
        if row is None:
            raise CaseNotFoundError(f"Case not found: {case_id}")
        transcripts = session.scalars(
            select(TranscriptRow).where(TranscriptRow.case_id == case_id)
        ).all()
        for transcript in transcripts:
            transcript.case_id = None
            transcript.session_label = None
            transcript.session_date = None
        session.delete(row)
        session.flush()

    def get_detail(self, session: Session, case_id: str) -> CaseDetail:
        case = self.get(session, case_id)
        transcripts = session.scalars(
            select(TranscriptRow)
            .where(TranscriptRow.case_id == case_id)
            .order_by(TranscriptRow.created_at.asc())
        ).all()
        transcripts = sorted(
            transcripts,
            key=lambda row: (
                row.session_date or row.created_at,
                row.created_at,
            ),
        )
        summaries: list[CaseTranscriptSummary] = []
        for transcript in transcripts:
            run_count = session.scalar(
                select(func.count())
                .select_from(WorkflowRunRow)
                .where(WorkflowRunRow.transcript_id == transcript.id)
            )
            summaries.append(
                CaseTranscriptSummary(
                    id=transcript.id,
                    title=transcript.title,
                    session_label=transcript.session_label,
                    session_date=transcript.session_date,
                    created_at=transcript.created_at,
                    analysis_ready=bool(transcript.analysis_ready),
                    workflow_run_count=int(run_count or 0),
                )
            )
        return CaseDetail(case=case, transcripts=summaries)

    def assign_transcript(
        self,
        session: Session,
        transcript_id: str,
        *,
        case_id: str | None,
        session_label: str | None = None,
        session_date: datetime | None = None,
    ) -> TranscriptRow:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            from backend.core.exceptions import TranscriptNotFoundError

            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        if case_id is not None:
            if session.get(CaseRow, case_id) is None:
                raise CaseNotFoundError(f"Case not found: {case_id}")
        row.case_id = case_id
        if session_label is not None:
            row.session_label = session_label or None
        if session_date is not None:
            row.session_date = session_date
        if case_id is None:
            row.session_label = None
            row.session_date = None
        session.flush()
        return row


def _from_row(row: CaseRow) -> Case:
    return Case(
        id=row.id,
        title=row.title,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
