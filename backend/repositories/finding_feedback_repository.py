"""Finding feedback persistence (v0.9 P6)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import CaseValidationError
from backend.db.models import FindingFeedbackRow, FindingRow


_ALLOWED_RATINGS = frozenset(
    {
        "helpful",
        "unhelpful",
        "unsure",
        # v1.3 structured feedback labels
        "not_helpful",
        "unsupported",
        "wrong_speaker",
        "wrong_evidence",
        "too_speculative",
        "too_clinical",
        "too_vague",
        "actionably_useful",
        "unsafe_framing",
        "pinned",
    }
)


class FindingFeedbackRepository:
    def create(
        self,
        session: Session,
        *,
        finding_key: str,
        rating: str,
        note: str | None = None,
        workflow_run_id: str | None = None,
        transcript_id: str | None = None,
        case_id: str | None = None,
    ) -> dict:
        rating_norm = rating.strip().lower()
        if rating_norm not in _ALLOWED_RATINGS:
            raise CaseValidationError(
                f"rating must be one of: {', '.join(sorted(_ALLOWED_RATINGS))}"
            )
        finding_row_id = None
        if ":" in finding_key and workflow_run_id:
            module_id, source_id = finding_key.split(":", 1)
            row = session.scalars(
                select(FindingRow).where(
                    FindingRow.workflow_run_id == workflow_run_id,
                    FindingRow.module_id == module_id,
                    FindingRow.source_id == source_id,
                )
            ).first()
            if row is not None:
                finding_row_id = row.id

        feedback_id = str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        session.add(
            FindingFeedbackRow(
                id=feedback_id,
                finding_row_id=finding_row_id,
                finding_key=finding_key,
                workflow_run_id=workflow_run_id,
                transcript_id=transcript_id,
                case_id=case_id,
                rating=rating_norm,
                note=note,
                created_at=now,
            )
        )
        session.flush()
        return {
            "id": feedback_id,
            "finding_key": finding_key,
            "finding_row_id": finding_row_id,
            "workflow_run_id": workflow_run_id,
            "transcript_id": transcript_id,
            "case_id": case_id,
            "rating": rating_norm,
            "note": note,
            "created_at": now.isoformat(),
        }

    def list_for_workflow(self, session: Session, workflow_run_id: str) -> list[dict]:
        rows = session.scalars(
            select(FindingFeedbackRow)
            .where(FindingFeedbackRow.workflow_run_id == workflow_run_id)
            .order_by(FindingFeedbackRow.created_at.desc())
        ).all()
        return [
            {
                "id": row.id,
                "finding_key": row.finding_key,
                "finding_row_id": row.finding_row_id,
                "workflow_run_id": row.workflow_run_id,
                "transcript_id": row.transcript_id,
                "case_id": row.case_id,
                "rating": row.rating,
                "note": row.note,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
