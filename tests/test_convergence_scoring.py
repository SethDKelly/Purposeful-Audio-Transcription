"""Deterministic convergence scoring (v0.8 P5)."""

from backend.db.base import get_session
from backend.db.models import ConstructRow
from backend.domain.enums import Confidence, ModuleRunStatus, SourceType
from backend.domain.finding import Construct
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.services.convergence_scoring_service import ConvergenceScoringService
from backend.services.graph_merge_service import GraphMergeService
from backend.services.transcript_service import TranscriptService
from sqlalchemy import select


def test_convergence_scoring_marks_multi_module_strong() -> None:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="score-test",
    )
    repo = ConstructRepository()
    module_runs = ModuleRunRepository()
    with get_session() as session:
        run_a = module_runs.create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-score",
        )
        run_a.status = ModuleRunStatus.COMPLETED.value
        module_runs.save(session, run_a)
        run_b = module_runs.create(
            session,
            module_id="gottman_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-score",
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

    GraphMergeService().merge_workflow_constructs("wf-score")
    scored = ConvergenceScoringService().score_workflow_constructs("wf-score")
    assert scored >= 1
    with get_session() as session:
        row = session.scalars(
            select(ConstructRow).where(
                ConstructRow.workflow_run_id == "wf-score",
                ConstructRow.is_canonical.is_(True),
            )
        ).one()
        assert row.convergence_score in {"strong", "moderate"}
        assert row.convergence_rationale_json
