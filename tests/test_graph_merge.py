"""Graph merge / deduplication (v0.8 P4)."""

from backend.db.base import get_session
from backend.db.models import ConstructRow
from backend.domain.enums import Confidence, ModuleRunStatus, SourceType
from backend.domain.finding import Construct
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.services.graph_merge_service import GraphMergeService
from backend.services.transcript_service import TranscriptService
from sqlalchemy import select


def _seed_constructs(workflow_run_id: str) -> None:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="merge-test",
    )
    repo = ConstructRepository()
    module_runs = ModuleRunRepository()
    with get_session() as session:
        run_a = module_runs.create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id=workflow_run_id,
        )
        run_a.status = ModuleRunStatus.COMPLETED.value
        module_runs.save(session, run_a)
        run_b = module_runs.create(
            session,
            module_id="gottman_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id=workflow_run_id,
        )
        run_b.status = ModuleRunStatus.COMPLETED.value
        module_runs.save(session, run_b)
        repo.replace_for_module_run(
            session,
            run_a,
            [
                Construct(
                    id="C001",
                    type="emotion",
                    label="Defensiveness",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )
        repo.replace_for_module_run(
            session,
            run_b,
            [
                Construct(
                    id="C010",
                    type="emotion",
                    label="defensive posture",
                    confidence=Confidence.HIGH,
                    evidence_quote_ids=["Q002"],
                )
            ],
        )


def test_graph_merge_absorbs_similar_constructs() -> None:
    _seed_constructs("wf-merge")
    result = GraphMergeService().merge_workflow_constructs("wf-merge")
    assert result.groups_merged == 1
    assert result.constructs_absorbed == 1
    with get_session() as session:
        rows = session.scalars(
            select(ConstructRow).where(ConstructRow.workflow_run_id == "wf-merge")
        ).all()
        canonical = [row for row in rows if row.is_canonical]
        absorbed = [row for row in rows if not row.is_canonical]
        assert len(canonical) == 1
        assert len(absorbed) == 1
        assert absorbed[0].merged_into_id == canonical[0].id
        assert canonical[0].confidence == Confidence.HIGH.value
