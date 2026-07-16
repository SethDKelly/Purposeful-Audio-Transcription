"""Persist and query normalized findings (v0.8 P1)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.db.models import (
    FindingAlternativeExplanationRow,
    FindingEvidenceQuoteRow,
    FindingRow,
)
from backend.domain.finding import Finding, ModuleRun


class FindingRepository:
    def replace_for_module_run(
        self,
        session: Session,
        run: ModuleRun,
        findings: list[Finding],
        *,
        module_version: str | None = None,
    ) -> list[str]:
        """Replace all findings for a module run. Returns persisted finding row IDs."""
        self.delete_for_module_run(session, run.id)
        now = datetime.now(UTC).replace(tzinfo=None)
        persisted_ids: list[str] = []
        for finding in findings:
            row_id = str(uuid.uuid4())
            session.add(
                FindingRow(
                    id=row_id,
                    source_id=finding.id,
                    module_run_id=run.id,
                    workflow_run_id=run.workflow_run_id,
                    module_id=run.module_id,
                    module_version=module_version,
                    type=_enum_value(finding.type),
                    title=finding.title,
                    summary=finding.summary,
                    confidence=_enum_value(finding.confidence),
                    limitations_json=json.dumps(finding.limitations) if finding.limitations else None,
                    construct_ids_json=(
                        json.dumps(finding.construct_ids) if finding.construct_ids else None
                    ),
                    created_at=now,
                )
            )
            for position, quote_id in enumerate(finding.evidence_quote_ids):
                session.add(
                    FindingEvidenceQuoteRow(
                        finding_id=row_id,
                        quote_id=quote_id,
                        position=position,
                    )
                )
            for position, text in enumerate(finding.alternative_explanations):
                session.add(
                    FindingAlternativeExplanationRow(
                        finding_id=row_id,
                        text=text,
                        position=position,
                    )
                )
            persisted_ids.append(row_id)
        session.flush()
        return persisted_ids

    def delete_for_module_run(self, session: Session, module_run_id: str) -> None:
        finding_ids = list(
            session.scalars(
                select(FindingRow.id).where(FindingRow.module_run_id == module_run_id)
            ).all()
        )
        if not finding_ids:
            return
        session.execute(
            delete(FindingEvidenceQuoteRow).where(
                FindingEvidenceQuoteRow.finding_id.in_(finding_ids)
            )
        )
        session.execute(
            delete(FindingAlternativeExplanationRow).where(
                FindingAlternativeExplanationRow.finding_id.in_(finding_ids)
            )
        )
        session.execute(delete(FindingRow).where(FindingRow.id.in_(finding_ids)))
        session.flush()

    def delete_for_module_runs(self, session: Session, module_run_ids: list[str]) -> None:
        if not module_run_ids:
            return
        finding_ids = list(
            session.scalars(
                select(FindingRow.id).where(FindingRow.module_run_id.in_(module_run_ids))
            ).all()
        )
        if not finding_ids:
            return
        session.execute(
            delete(FindingEvidenceQuoteRow).where(
                FindingEvidenceQuoteRow.finding_id.in_(finding_ids)
            )
        )
        session.execute(
            delete(FindingAlternativeExplanationRow).where(
                FindingAlternativeExplanationRow.finding_id.in_(finding_ids)
            )
        )
        session.execute(delete(FindingRow).where(FindingRow.id.in_(finding_ids)))
        session.flush()

    def list_by_workflow_run_id(self, session: Session, workflow_run_id: str) -> list[dict]:
        rows = session.scalars(
            select(FindingRow)
            .where(FindingRow.workflow_run_id == workflow_run_id)
            .order_by(FindingRow.created_at, FindingRow.source_id)
        ).all()
        if not rows:
            return []
        finding_ids = [row.id for row in rows]
        quote_rows = session.scalars(
            select(FindingEvidenceQuoteRow)
            .where(FindingEvidenceQuoteRow.finding_id.in_(finding_ids))
            .order_by(FindingEvidenceQuoteRow.position)
        ).all()
        alt_rows = session.scalars(
            select(FindingAlternativeExplanationRow)
            .where(FindingAlternativeExplanationRow.finding_id.in_(finding_ids))
            .order_by(FindingAlternativeExplanationRow.position)
        ).all()
        quotes_by_finding: dict[str, list[str]] = {fid: [] for fid in finding_ids}
        for quote in quote_rows:
            quotes_by_finding.setdefault(quote.finding_id, []).append(quote.quote_id)
        alts_by_finding: dict[str, list[str]] = {fid: [] for fid in finding_ids}
        for alt in alt_rows:
            alts_by_finding.setdefault(alt.finding_id, []).append(alt.text)

        results: list[dict] = []
        for row in rows:
            source_id = row.source_id
            results.append(
                {
                    "row_id": row.id,
                    "finding_key": f"{row.module_id}:{source_id}",
                    "module_id": row.module_id,
                    "module_run_id": row.module_run_id,
                    "workflow_run_id": row.workflow_run_id,
                    "module_version": row.module_version,
                    "id": source_id,
                    "type": row.type,
                    "title": row.title,
                    "summary": row.summary,
                    "confidence": row.confidence,
                    "evidence_quote_ids": quotes_by_finding.get(row.id, []),
                    "alternative_explanations": alts_by_finding.get(row.id, []),
                    "limitations": _loads_list(row.limitations_json),
                    "construct_ids": _loads_list(row.construct_ids_json),
                }
            )
        return results

    def count_by_workflow_run_id(self, session: Session, workflow_run_id: str) -> int:
        rows = session.scalars(
            select(FindingRow.id).where(FindingRow.workflow_run_id == workflow_run_id)
        ).all()
        return len(rows)


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []
