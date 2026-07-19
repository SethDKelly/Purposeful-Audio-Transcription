"""Safety event persistence (v2.0)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import SafetyEventRow


class SafetyEventRepository:
    def create(
        self,
        session: Session,
        *,
        event_type: str,
        risk_level: str,
        transcript_id: str | None = None,
        workflow_run_id: str | None = None,
        categories: list[str] | None = None,
        details: dict | None = None,
    ) -> dict:
        event_id = str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        session.add(
            SafetyEventRow(
                id=event_id,
                transcript_id=transcript_id,
                workflow_run_id=workflow_run_id,
                event_type=event_type,
                risk_level=risk_level,
                categories_json=json.dumps(categories or []),
                details_json=json.dumps(details or {}),
                created_at=now,
            )
        )
        session.flush()
        return {
            "id": event_id,
            "transcript_id": transcript_id,
            "workflow_run_id": workflow_run_id,
            "event_type": event_type,
            "risk_level": risk_level,
            "categories": categories or [],
            "details": details or {},
            "created_at": now.isoformat(),
        }

    def list_for_transcript(self, session: Session, transcript_id: str) -> list[dict]:
        rows = session.scalars(
            select(SafetyEventRow)
            .where(SafetyEventRow.transcript_id == transcript_id)
            .order_by(SafetyEventRow.created_at.desc())
        ).all()
        return [_row_to_dict(r) for r in rows]

    def list_for_run(self, session: Session, workflow_run_id: str) -> list[dict]:
        rows = session.scalars(
            select(SafetyEventRow)
            .where(SafetyEventRow.workflow_run_id == workflow_run_id)
            .order_by(SafetyEventRow.created_at.desc())
        ).all()
        return [_row_to_dict(r) for r in rows]


def _row_to_dict(row: SafetyEventRow) -> dict:
    try:
        categories = json.loads(row.categories_json or "[]")
    except json.JSONDecodeError:
        categories = []
    try:
        details = json.loads(row.details_json or "{}")
    except json.JSONDecodeError:
        details = {}
    return {
        "id": row.id,
        "transcript_id": row.transcript_id,
        "workflow_run_id": row.workflow_run_id,
        "event_type": row.event_type,
        "risk_level": row.risk_level,
        "categories": categories,
        "details": details,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


safety_event_repository = SafetyEventRepository()
