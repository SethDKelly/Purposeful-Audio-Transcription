"""Persist and query normalized constructs (v0.8 P2)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.core.ontology_registry import OntologyRegistry, ontology_registry
from backend.db.models import ConstructEvidenceQuoteRow, ConstructRow, ConstructSourceRow
from backend.domain.finding import Construct, ModuleRun


class ConstructRepository:
    def __init__(self, ontology: OntologyRegistry | None = None) -> None:
        self._ontology = ontology or ontology_registry

    def replace_for_module_run(
        self,
        session: Session,
        run: ModuleRun,
        constructs: list[Construct],
    ) -> list[str]:
        self.delete_for_module_run(session, run.id)
        now = datetime.now(UTC).replace(tzinfo=None)
        persisted_ids: list[str] = []
        for construct in constructs:
            resolved = self._ontology.resolve_construct(construct.type)
            ontology_type = resolved or construct.type
            warning = None
            if resolved is None:
                warning = f"Unknown construct type: {construct.type}"
            row_id = str(uuid.uuid4())
            session.add(
                ConstructRow(
                    id=row_id,
                    source_id=construct.id,
                    module_run_id=run.id,
                    workflow_run_id=run.workflow_run_id,
                    module_id=run.module_id,
                    ontology_type=ontology_type,
                    label=construct.label,
                    description=construct.description,
                    confidence=_enum_value(construct.confidence),
                    ontology_resolved=resolved is not None,
                    ontology_warning=warning,
                    merged_into_id=None,
                    is_canonical=True,
                    convergence_score=None,
                    convergence_rationale_json=None,
                    created_at=now,
                )
            )
            for position, quote_id in enumerate(construct.evidence_quote_ids):
                session.add(
                    ConstructEvidenceQuoteRow(
                        construct_id=row_id,
                        quote_id=quote_id,
                        position=position,
                    )
                )
            session.add(
                ConstructSourceRow(
                    construct_id=row_id,
                    module_run_id=run.id,
                    module_id=run.module_id,
                    source_construct_id=construct.id,
                )
            )
            persisted_ids.append(row_id)
        session.flush()
        return persisted_ids

    def delete_for_module_run(self, session: Session, module_run_id: str) -> None:
        construct_ids = list(
            session.scalars(
                select(ConstructRow.id).where(ConstructRow.module_run_id == module_run_id)
            ).all()
        )
        self._delete_by_ids(session, construct_ids)

    def delete_for_module_runs(self, session: Session, module_run_ids: list[str]) -> None:
        if not module_run_ids:
            return
        construct_ids = list(
            session.scalars(
                select(ConstructRow.id).where(ConstructRow.module_run_id.in_(module_run_ids))
            ).all()
        )
        self._delete_by_ids(session, construct_ids)

    def _delete_by_ids(self, session: Session, construct_ids: list[str]) -> None:
        if not construct_ids:
            return
        session.execute(
            delete(ConstructEvidenceQuoteRow).where(
                ConstructEvidenceQuoteRow.construct_id.in_(construct_ids)
            )
        )
        session.execute(
            delete(ConstructSourceRow).where(
                ConstructSourceRow.construct_id.in_(construct_ids)
            )
        )
        session.execute(delete(ConstructRow).where(ConstructRow.id.in_(construct_ids)))
        session.flush()

    def list_by_workflow_run_id(
        self,
        session: Session,
        workflow_run_id: str,
        *,
        canonical_only: bool = False,
    ) -> list[dict]:
        query = select(ConstructRow).where(ConstructRow.workflow_run_id == workflow_run_id)
        if canonical_only:
            query = query.where(ConstructRow.is_canonical.is_(True))
        rows = session.scalars(
            query.order_by(ConstructRow.created_at, ConstructRow.source_id)
        ).all()
        if not rows:
            return []
        construct_ids = [row.id for row in rows]
        quote_rows = session.scalars(
            select(ConstructEvidenceQuoteRow)
            .where(ConstructEvidenceQuoteRow.construct_id.in_(construct_ids))
            .order_by(ConstructEvidenceQuoteRow.position)
        ).all()
        source_rows = session.scalars(
            select(ConstructSourceRow).where(
                ConstructSourceRow.construct_id.in_(construct_ids)
            )
        ).all()
        quotes_by: dict[str, list[str]] = {cid: [] for cid in construct_ids}
        for quote in quote_rows:
            quotes_by.setdefault(quote.construct_id, []).append(quote.quote_id)
        sources_by: dict[str, list[dict]] = {cid: [] for cid in construct_ids}
        for source in source_rows:
            sources_by.setdefault(source.construct_id, []).append(
                {
                    "module_run_id": source.module_run_id,
                    "module_id": source.module_id,
                    "source_construct_id": source.source_construct_id,
                }
            )
        return [
            {
                "row_id": row.id,
                "source_id": row.source_id,
                "module_run_id": row.module_run_id,
                "workflow_run_id": row.workflow_run_id,
                "module_id": row.module_id,
                "ontology_type": row.ontology_type,
                "label": row.label,
                "description": row.description,
                "confidence": row.confidence,
                "ontology_resolved": row.ontology_resolved,
                "ontology_warning": row.ontology_warning,
                "evidence_quote_ids": quotes_by.get(row.id, []),
                "sources": sources_by.get(row.id, []),
                "merged_into_id": row.merged_into_id,
                "is_canonical": row.is_canonical,
                "convergence_score": row.convergence_score,
            }
            for row in rows
        ]


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)
