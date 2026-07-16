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

    def synthesis_handoff(self, workflow_run_id: str) -> dict:
        """Compact structured inventory for meta-synthesis prompts."""
        inventory = self.inventory(workflow_run_id)
        robust = []
        exploratory = []
        for construct in inventory["constructs"]:
            item = {
                "id": construct.get("row_id"),
                "source_id": construct.get("source_id"),
                "type": construct.get("ontology_type"),
                "label": construct.get("label"),
                "confidence": construct.get("confidence"),
                "convergence_score": construct.get("convergence_score"),
                "evidence_quote_ids": construct.get("evidence_quote_ids", []),
                "module_ids": sorted(
                    {s.get("module_id") for s in construct.get("sources", []) if s.get("module_id")}
                ),
            }
            score = (construct.get("convergence_score") or "").lower()
            if score in {"strong", "moderate"}:
                robust.append(item)
            else:
                exploratory.append(item)
        return {
            "workflow_run_id": workflow_run_id,
            "findings": [
                {
                    "finding_key": f.get("finding_key"),
                    "id": f.get("id"),
                    "type": f.get("type"),
                    "title": f.get("title"),
                    "summary": f.get("summary"),
                    "confidence": f.get("confidence"),
                    "module_id": f.get("module_id"),
                    "evidence_quote_ids": f.get("evidence_quote_ids", []),
                }
                for f in inventory["findings"]
            ],
            "robust_constructs": robust,
            "exploratory_constructs": exploratory,
            "relationships": [
                {
                    "id": r.get("row_id"),
                    "source_construct_id": r.get("source_construct_id"),
                    "target_construct_id": r.get("target_construct_id"),
                    "relationship_type": r.get("relationship_type"),
                    "confidence": r.get("confidence"),
                    "module_id": r.get("module_id"),
                }
                for r in inventory["relationships"]
            ],
            "guidance": (
                "Primary input is this structured inventory. Cite finding_key and construct "
                "ids. Treat robust_constructs as higher priority than exploratory_constructs. "
                "Module output blobs are secondary detail only."
            ),
        }


structured_graph_service = StructuredGraphService()
