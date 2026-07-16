"""Synthesis handoff over structured inventory (v0.8 P7)."""

from backend.db.base import get_session
from backend.domain.enums import Confidence, ModuleRunStatus, SourceType
from backend.domain.finding import Construct, Finding
from backend.domain.enums import FindingType
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.services.convergence_scoring_service import ConvergenceScoringService
from backend.services.graph_merge_service import GraphMergeService
from backend.services.structured_graph_service import StructuredGraphService
from backend.services.synthesis_preprocessor import SynthesisPreprocessor
from backend.services.transcript_service import TranscriptService
from backend.domain.finding import ModuleRun


def test_synthesis_handoff_separates_robust_and_exploratory() -> None:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="synth-handoff",
    )
    with get_session() as session:
        run_a = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-synth",
        )
        run_a.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run_a)
        run_b = ModuleRunRepository().create(
            session,
            module_id="gottman_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-synth",
        )
        run_b.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run_b)
        FindingRepository().replace_for_module_run(
            session,
            run_a,
            [
                Finding(
                    id="F001",
                    module_run_id=run_a.id,
                    type=FindingType.OBSERVATION,
                    title="Greeting",
                    summary="Warm greeting.",
                    confidence=Confidence.HIGH,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )
        ConstructRepository().replace_for_module_run(
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
        ConstructRepository().replace_for_module_run(
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

    GraphMergeService().merge_workflow_constructs("wf-synth")
    ConvergenceScoringService().score_workflow_constructs("wf-synth")
    handoff = StructuredGraphService().synthesis_handoff("wf-synth")
    assert handoff["findings"]
    assert handoff["robust_constructs"] or handoff["exploratory_constructs"]
    assert "structured inventory" in handoff["guidance"].lower()

    preprocessed = SynthesisPreprocessor().process(
        [
            ModuleRun(
                id=run_a.id,
                module_id="nvc_analysis",
                transcript_id=bundle.transcript.id,
                workflow_run_id="wf-synth",
                status=ModuleRunStatus.COMPLETED.value,
                parsed_output={
                    "executive_summary": "A",
                    "findings": [
                        {
                            "id": "F001",
                            "type": "observation",
                            "title": "Greeting",
                            "summary": "Warm greeting.",
                            "confidence": "high",
                            "evidence_quote_ids": ["Q001"],
                        }
                    ],
                },
                created_at=run_a.created_at,
            )
        ],
        workflow_run_id="wf-synth",
    )
    assert preprocessed.structured_inventory is not None
    assert preprocessed.robust_construct_ids or preprocessed.exploratory_construct_ids
