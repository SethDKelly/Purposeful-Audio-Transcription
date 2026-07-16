"""Merge near-duplicate constructs across modules (v0.8 P4)."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.base import get_session
from backend.db.models import ConstructEvidenceQuoteRow, ConstructRow, ConstructSourceRow
from backend.domain.enums import Confidence

_CONFIDENCE_RANK = {
    Confidence.HIGH.value: 3,
    Confidence.MODERATE.value: 2,
    Confidence.LOW.value: 1,
    Confidence.EXPLORATORY.value: 0,
    "high": 3,
    "moderate": 2,
    "low": 1,
    "exploratory": 0,
}


@dataclass(frozen=True)
class MergeResult:
    workflow_run_id: str
    groups_merged: int
    constructs_absorbed: int


class GraphMergeService:
    def merge_workflow_constructs(self, workflow_run_id: str) -> MergeResult:
        with get_session() as session:
            return self.merge_workflow_constructs_in_session(session, workflow_run_id)

    def merge_workflow_constructs_in_session(
        self, session: Session, workflow_run_id: str
    ) -> MergeResult:
        rows = list(
            session.scalars(
                select(ConstructRow).where(
                    ConstructRow.workflow_run_id == workflow_run_id,
                    ConstructRow.is_canonical.is_(True),
                    ConstructRow.merged_into_id.is_(None),
                )
            ).all()
        )
        if len(rows) < 2:
            return MergeResult(workflow_run_id, 0, 0)

        by_type: dict[str, list[ConstructRow]] = defaultdict(list)
        for row in rows:
            by_type[row.ontology_type].append(row)

        groups_merged = 0
        absorbed = 0
        for group in by_type.values():
            clusters = _cluster_similar(group)
            for cluster in clusters:
                if len(cluster) < 2:
                    continue
                primary = _pick_primary(cluster)
                others = [row for row in cluster if row.id != primary.id]
                self._absorb(session, primary, others)
                groups_merged += 1
                absorbed += len(others)

        session.flush()
        return MergeResult(workflow_run_id, groups_merged, absorbed)

    def _absorb(
        self,
        session: Session,
        primary: ConstructRow,
        others: list[ConstructRow],
    ) -> None:
        existing_quotes = {
            q.quote_id
            for q in session.scalars(
                select(ConstructEvidenceQuoteRow).where(
                    ConstructEvidenceQuoteRow.construct_id == primary.id
                )
            ).all()
        }
        next_pos = len(existing_quotes)
        for other in others:
            other_quotes = session.scalars(
                select(ConstructEvidenceQuoteRow).where(
                    ConstructEvidenceQuoteRow.construct_id == other.id
                )
            ).all()
            for quote in other_quotes:
                if quote.quote_id in existing_quotes:
                    continue
                session.add(
                    ConstructEvidenceQuoteRow(
                        construct_id=primary.id,
                        quote_id=quote.quote_id,
                        position=next_pos,
                    )
                )
                existing_quotes.add(quote.quote_id)
                next_pos += 1

            other_sources = session.scalars(
                select(ConstructSourceRow).where(ConstructSourceRow.construct_id == other.id)
            ).all()
            for source in other_sources:
                session.add(
                    ConstructSourceRow(
                        construct_id=primary.id,
                        module_run_id=source.module_run_id,
                        module_id=source.module_id,
                        source_construct_id=source.source_construct_id,
                    )
                )

            other.is_canonical = False
            other.merged_into_id = primary.id

        if _CONFIDENCE_RANK.get(primary.confidence, 0) < max(
            _CONFIDENCE_RANK.get(o.confidence, 0) for o in others
        ):
            best = max(others, key=lambda row: _CONFIDENCE_RANK.get(row.confidence, 0))
            primary.confidence = best.confidence

        labels = [primary.label] + [o.label for o in others]
        if len({label.casefold() for label in labels}) > 1:
            primary.description = (
                (primary.description or primary.label)
                + " | merged labels: "
                + "; ".join(sorted({label for label in labels if label != primary.label}))
            )


def _normalize_label(label: str) -> str:
    text = label.casefold().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokens(label: str) -> set[str]:
    return {token for token in _normalize_label(label).split() if len(token) > 1}


def _similar(a: ConstructRow, b: ConstructRow) -> bool:
    na = _normalize_label(a.label)
    nb = _normalize_label(b.label)
    if not na or not nb:
        return False
    if na == nb or na in nb or nb in na:
        return True
    ta, tb = _tokens(a.label), _tokens(b.label)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / len(ta | tb)
    if overlap >= 0.8:
        return True
    stems_a = {token[:6] for token in ta if len(token) >= 5}
    stems_b = {token[:6] for token in tb if len(token) >= 5}
    return bool(stems_a and stems_b and stems_a & stems_b)


def _cluster_similar(rows: list[ConstructRow]) -> list[list[ConstructRow]]:
    clusters: list[list[ConstructRow]] = []
    for row in rows:
        placed = False
        for cluster in clusters:
            if any(_similar(row, member) for member in cluster):
                cluster.append(row)
                placed = True
                break
        if not placed:
            clusters.append([row])
    return clusters


def _pick_primary(cluster: list[ConstructRow]) -> ConstructRow:
    return sorted(
        cluster,
        key=lambda row: (
            -_CONFIDENCE_RANK.get(row.confidence, 0),
            row.created_at,
            row.id,
        ),
    )[0]


graph_merge_service = GraphMergeService()
