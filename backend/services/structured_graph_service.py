"""Structured graph inventory over normalized tables (v0.8 P6)."""

from __future__ import annotations

from backend.db.base import get_session
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.relationship_repository import ConstructRelationshipRepository


class StructuredGraphService:
    def __init__(
        self,
        findings: FindingRepository | None = None,
        constructs: ConstructRepository | None = None,
        relationships: ConstructRelationshipRepository | None = None,
    ) -> None:
        self._findings = findings or FindingRepository()
        self._constructs = constructs or ConstructRepository()
        self._relationships = relationships or ConstructRelationshipRepository()

    def inventory(self, workflow_run_id: str) -> dict:
        with get_session() as session:
            findings = self._findings.list_by_workflow_run_id(session, workflow_run_id)
            constructs = self._constructs.list_by_workflow_run_id(
                session, workflow_run_id, canonical_only=True
            )
            relationships = self._relationships.list_by_workflow_run_id(
                session, workflow_run_id
            )
        return {
            "workflow_run_id": workflow_run_id,
            "findings": findings,
            "constructs": constructs,
            "relationships": relationships,
            "counts": {
                "findings": len(findings),
                "constructs": len(constructs),
                "relationships": len(relationships),
            },
        }


structured_graph_service = StructuredGraphService()
