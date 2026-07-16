"""Deterministic convergence scoring for constructs (v0.8 P5)."""

from __future__ import annotations

import json
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.base import get_session
from backend.db.models import ConstructRelationshipRow, ConstructRow, ConstructSourceRow
from backend.domain.enums import Confidence

_CONFIDENCE_RANK = {
    Confidence.HIGH.value: 3,
    Confidence.MODERATE.value: 2,
    Confidence.LOW.value: 1,
    Confidence.EXPLORATORY.value: 0,
}


class ConvergenceScoringService:
    def score_workflow_constructs(self, workflow_run_id: str) -> int:
        with get_session() as session:
            return self.score_workflow_constructs_in_session(session, workflow_run_id)

    def score_workflow_constructs_in_session(
        self, session: Session, workflow_run_id: str
    ) -> int:
        constructs = list(
            session.scalars(
                select(ConstructRow).where(
                    ConstructRow.workflow_run_id == workflow_run_id,
                    ConstructRow.is_canonical.is_(True),
                )
            ).all()
        )
        if not constructs:
            return 0

        construct_ids = [row.id for row in constructs]
        sources = session.scalars(
            select(ConstructSourceRow).where(
                ConstructSourceRow.construct_id.in_(construct_ids)
            )
        ).all()
        sources_by: dict[str, list[ConstructSourceRow]] = defaultdict(list)
        for source in sources:
            sources_by[source.construct_id].append(source)

        relationships = session.scalars(
            select(ConstructRelationshipRow).where(
                ConstructRelationshipRow.workflow_run_id == workflow_run_id
            )
        ).all()
        contradict_counts: dict[str, int] = defaultdict(int)
        source_id_to_row = {row.source_id: row.id for row in constructs}
        row_ids = set(construct_ids)
        for rel in relationships:
            if rel.relationship_type != "contradicts":
                continue
            endpoints: set[str] = set()
            if rel.source_construct_row_id and rel.source_construct_row_id in row_ids:
                endpoints.add(rel.source_construct_row_id)
            if rel.target_construct_row_id and rel.target_construct_row_id in row_ids:
                endpoints.add(rel.target_construct_row_id)
            if rel.source_construct_source_id in source_id_to_row:
                endpoints.add(source_id_to_row[rel.source_construct_source_id])
            if rel.target_construct_source_id in source_id_to_row:
                endpoints.add(source_id_to_row[rel.target_construct_source_id])
            for endpoint in endpoints:
                contradict_counts[endpoint] += 1

        scored = 0
        for row in constructs:
            module_ids = {s.module_id for s in sources_by.get(row.id, [])}
            module_count = max(len(module_ids), 1)
            conf_rank = _CONFIDENCE_RANK.get(row.confidence, 0)
            contradictions = contradict_counts.get(row.id, 0)
            score, rationale = _score(
                module_count=module_count,
                confidence_rank=conf_rank,
                contradictions=contradictions,
                evidence_present=True,
            )
            row.convergence_score = score
            row.convergence_rationale_json = json.dumps(rationale)
            scored += 1
        session.flush()
        return scored


def _score(
    *,
    module_count: int,
    confidence_rank: int,
    contradictions: int,
    evidence_present: bool,
) -> tuple[str, dict]:
    rationale = {
        "supporting_module_count": module_count,
        "confidence_rank": confidence_rank,
        "contradictions": contradictions,
        "evidence_present": evidence_present,
    }
    if contradictions > 0:
        return "contested", {**rationale, "reason": "contradicting relationships present"}
    if module_count >= 3 and confidence_rank >= 2 and evidence_present:
        return "strong", {**rationale, "reason": "multi-module agreement with solid confidence"}
    if module_count >= 2 and confidence_rank >= 2:
        return "moderate", {**rationale, "reason": "agreement across modules"}
    if module_count >= 2:
        return "moderate", {**rationale, "reason": "cross-module support with modest confidence"}
    if confidence_rank >= 3 and evidence_present:
        return "moderate", {**rationale, "reason": "single-module high confidence with evidence"}
    if confidence_rank <= 1:
        return "weak", {**rationale, "reason": "low confidence or exploratory only"}
    return "weak", {**rationale, "reason": "single-module support"}


convergence_scoring_service = ConvergenceScoringService()
