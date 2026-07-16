"""Persist and query construct relationships (v0.8 P3)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.core.ontology_registry import OntologyRegistry, ontology_registry
from backend.db.models import (
    ConstructRelationshipEvidenceQuoteRow,
    ConstructRelationshipRow,
    ConstructRow,
)
from backend.domain.finding import ConstructRelationship, ModuleRun


class ConstructRelationshipRepository:
    def __init__(self, ontology: OntologyRegistry | None = None) -> None:
        self._ontology = ontology or ontology_registry

    def replace_for_module_run(
        self,
        session: Session,
        run: ModuleRun,
        relationships: list[ConstructRelationship],
    ) -> list[str]:
        self.delete_for_module_run(session, run.id)
        construct_rows = session.scalars(
            select(ConstructRow).where(ConstructRow.module_run_id == run.id)
        ).all()
        by_source_id = {row.source_id: row.id for row in construct_rows}
        now = datetime.now(UTC).replace(tzinfo=None)
        persisted: list[str] = []
        for rel in relationships:
            resolved = self._ontology.resolve_relationship(_enum_value(rel.relationship_type))
            rel_type = resolved or _enum_value(rel.relationship_type)
            ontology_warning = None
            if resolved is None:
                ontology_warning = f"Unknown relationship type: {rel.relationship_type}"

            source_row = by_source_id.get(rel.source_construct_id)
            target_row = by_source_id.get(rel.target_construct_id)
            link_warnings: list[str] = []
            if source_row is None:
                link_warnings.append(f"Missing source construct: {rel.source_construct_id}")
            if target_row is None:
                link_warnings.append(f"Missing target construct: {rel.target_construct_id}")

            row_id = str(uuid.uuid4())
            session.add(
                ConstructRelationshipRow(
                    id=row_id,
                    source_id=rel.id,
                    module_run_id=run.id,
                    workflow_run_id=run.workflow_run_id,
                    module_id=run.module_id,
                    source_construct_source_id=rel.source_construct_id,
                    target_construct_source_id=rel.target_construct_id,
                    source_construct_row_id=source_row,
                    target_construct_row_id=target_row,
                    relationship_type=rel_type,
                    confidence=_enum_value(rel.confidence),
                    ontology_resolved=resolved is not None,
                    ontology_warning=ontology_warning,
                    link_warning="; ".join(link_warnings) if link_warnings else None,
                    created_at=now,
                )
            )
            persisted.append(row_id)
        session.flush()
        return persisted

    def delete_for_module_run(self, session: Session, module_run_id: str) -> None:
        rel_ids = list(
            session.scalars(
                select(ConstructRelationshipRow.id).where(
                    ConstructRelationshipRow.module_run_id == module_run_id
                )
            ).all()
        )
        self._delete_by_ids(session, rel_ids)

    def delete_for_module_runs(self, session: Session, module_run_ids: list[str]) -> None:
        if not module_run_ids:
            return
        rel_ids = list(
            session.scalars(
                select(ConstructRelationshipRow.id).where(
                    ConstructRelationshipRow.module_run_id.in_(module_run_ids)
                )
            ).all()
        )
        self._delete_by_ids(session, rel_ids)

    def _delete_by_ids(self, session: Session, rel_ids: list[str]) -> None:
        if not rel_ids:
            return
        session.execute(
            delete(ConstructRelationshipEvidenceQuoteRow).where(
                ConstructRelationshipEvidenceQuoteRow.relationship_id.in_(rel_ids)
            )
        )
        session.execute(
            delete(ConstructRelationshipRow).where(ConstructRelationshipRow.id.in_(rel_ids))
        )
        session.flush()

    def list_by_workflow_run_id(self, session: Session, workflow_run_id: str) -> list[dict]:
        rows = session.scalars(
            select(ConstructRelationshipRow)
            .where(ConstructRelationshipRow.workflow_run_id == workflow_run_id)
            .order_by(ConstructRelationshipRow.created_at, ConstructRelationshipRow.source_id)
        ).all()
        return [
            {
                "row_id": row.id,
                "source_id": row.source_id,
                "module_run_id": row.module_run_id,
                "workflow_run_id": row.workflow_run_id,
                "module_id": row.module_id,
                "source_construct_id": row.source_construct_source_id,
                "target_construct_id": row.target_construct_source_id,
                "source_construct_row_id": row.source_construct_row_id,
                "target_construct_row_id": row.target_construct_row_id,
                "relationship_type": row.relationship_type,
                "confidence": row.confidence,
                "ontology_resolved": row.ontology_resolved,
                "ontology_warning": row.ontology_warning,
                "link_warning": row.link_warning,
            }
            for row in rows
        ]


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)
