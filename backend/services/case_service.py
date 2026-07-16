"""Case service (v0.9 P1)."""

from __future__ import annotations

from datetime import datetime

from backend.db.base import get_session
from backend.domain.case import Case, CaseDetail
from backend.repositories.case_repository import CaseRepository


class CaseService:
    def __init__(self, repository: CaseRepository | None = None) -> None:
        self._repository = repository or CaseRepository()

    def create(self, *, title: str, notes: str | None = None) -> Case:
        with get_session() as session:
            return self._repository.create(session, title=title, notes=notes)

    def list(self) -> list[Case]:
        with get_session() as session:
            return self._repository.list(session)

    def get(self, case_id: str) -> Case:
        with get_session() as session:
            return self._repository.get(session, case_id)

    def get_detail(self, case_id: str) -> CaseDetail:
        with get_session() as session:
            return self._repository.get_detail(session, case_id)

    def update(
        self,
        case_id: str,
        *,
        title: str | None = None,
        notes: str | None = None,
    ) -> Case:
        with get_session() as session:
            return self._repository.update(session, case_id, title=title, notes=notes)

    def delete(self, case_id: str) -> None:
        with get_session() as session:
            self._repository.delete(session, case_id)

    def assign_transcript(
        self,
        transcript_id: str,
        *,
        case_id: str | None,
        session_label: str | None = None,
        session_date: datetime | None = None,
    ) -> dict:
        with get_session() as session:
            row = self._repository.assign_transcript(
                session,
                transcript_id,
                case_id=case_id,
                session_label=session_label,
                session_date=session_date,
            )
            return {
                "transcript_id": row.id,
                "case_id": row.case_id,
                "session_label": row.session_label,
                "session_date": row.session_date.isoformat() if row.session_date else None,
            }


case_service = CaseService()
