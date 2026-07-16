"""Normalized constructs persistence (v0.8 P2)."""

from sqlalchemy import select

from backend.db.base import get_session
from backend.db.models import ConstructRow
from backend.domain.enums import Confidence, ModuleRunStatus, SourceType
from backend.domain.finding import Construct
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.exploration_service import ExplorationService
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService


def _sample_construct(*, construct_id: str = "C001", ctype: str = "emotion") -> Construct:
    return Construct(
        id=construct_id,
        type=ctype,
        label="Defensiveness",
        description="Protective posture when accountability is raised.",
        confidence=Confidence.MODERATE,
        evidence_quote_ids=["Q001"],
    )


def _create_run(*, module_id: str, workflow_run_id: str):
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="construct-persist",
    )
    with get_session() as session:
        run = ModuleRunRepository().create(
            session,
            module_id=module_id,
            transcript_id=bundle.transcript.id,
            workflow_run_id=workflow_run_id,
        )
        run.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run)
        return run


def test_construct_repository_validates_ontology() -> None:
    repo = ConstructRepository()
    run = _create_run(module_id="nvc_analysis", workflow_run_id="wf-c1")
    with get_session() as session:
        repo.replace_for_module_run(
            session,
            run,
            [
                _sample_construct(),
                _sample_construct(construct_id="C002", ctype="not_a_real_type"),
            ],
        )
        listed = repo.list_by_workflow_run_id(session, "wf-c1")
        assert len(listed) == 2
        by_id = {item["source_id"]: item for item in listed}
        assert by_id["C001"]["ontology_resolved"] is True
        assert by_id["C001"]["ontology_type"] == "emotion"
        assert by_id["C002"]["ontology_resolved"] is False
        assert by_id["C002"]["ontology_warning"]


def test_module_runner_persists_constructs() -> None:
    run = _create_run(module_id="gottman_analysis", workflow_run_id="wf-c2")
    output = ModuleRunOutput(
        module_id="gottman_analysis",
        module_version="1.0.0",
        executive_summary="Summary",
        findings=[],
        constructs=[_sample_construct()],
        relationships=[],
    )
    ModuleRunner()._complete_run(run, output, safety_flags=[])
    with get_session() as session:
        rows = session.scalars(
            select(ConstructRow).where(ConstructRow.workflow_run_id == "wf-c2")
        ).all()
        assert len(rows) == 1
        assert rows[0].label == "Defensiveness"


def test_knowledge_graph_prefers_normalized_constructs() -> None:
    run = _create_run(module_id="systems_analysis", workflow_run_id="wf-c3")
    with get_session() as session:
        ConstructRepository().replace_for_module_run(
            session, run, [_sample_construct(construct_id="C010")]
        )
    graph = ExplorationService().get_knowledge_graph("wf-c3")
    assert graph["source"] == "normalized"
    assert len(graph["nodes"]) == 1
    assert graph["nodes"][0]["id"] == "systems_analysis:C010"
