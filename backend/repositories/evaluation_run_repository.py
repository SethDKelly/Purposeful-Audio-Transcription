"""Evaluation run persistence (v2.0)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import EvaluationRunRow


class EvaluationRunRepository:
    def create(
        self,
        session: Session,
        *,
        kind: str,
        gate_passed: bool,
        fixture_id: str | None = None,
        module_id: str | None = None,
        summary: dict | None = None,
    ) -> dict:
        run_id = str(uuid.uuid4())
        now = datetime.now(UTC).replace(tzinfo=None)
        summary_json = json.dumps(summary or {})
        session.add(
            EvaluationRunRow(
                id=run_id,
                kind=kind,
                fixture_id=fixture_id,
                module_id=module_id,
                gate_passed=gate_passed,
                summary_json=summary_json,
                created_at=now,
            )
        )
        session.flush()
        return {
            "id": run_id,
            "kind": kind,
            "fixture_id": fixture_id,
            "module_id": module_id,
            "gate_passed": gate_passed,
            "summary": summary or {},
            "created_at": now.isoformat(),
        }

    def list_recent(self, session: Session, *, limit: int = 50) -> list[dict]:
        rows = session.scalars(
            select(EvaluationRunRow).order_by(EvaluationRunRow.created_at.desc()).limit(limit)
        ).all()
        return [_row_to_dict(r) for r in rows]

    def get(self, session: Session, run_id: str) -> dict | None:
        row = session.get(EvaluationRunRow, run_id)
        return _row_to_dict(row) if row else None


def _row_to_dict(row: EvaluationRunRow) -> dict:
    try:
        summary = json.loads(row.summary_json or "{}")
    except json.JSONDecodeError:
        summary = {}
    return {
        "id": row.id,
        "kind": row.kind,
        "fixture_id": row.fixture_id,
        "module_id": row.module_id,
        "gate_passed": row.gate_passed,
        "summary": summary,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


evaluation_run_repository = EvaluationRunRepository()
