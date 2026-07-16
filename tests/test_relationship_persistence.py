"""Normalized construct relationship persistence (v0.8 P3)."""

from backend.db.base import get_session
from backend.domain.enums import Confidence, ModuleRunStatus, RelationshipType, SourceType
from backend.domain.finding import Construct, ConstructRelationship
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.repositories.relationship_repository import ConstructRelationshipRepository
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.exploration_service import ExplorationService
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService


def _create_run(*, module_id: str, workflow_run_id: str):
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="rel-persist",
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


def test_relationship_repository_links_and_warns() -> None:
    constructs = ConstructRepository()
    relationships = ConstructRelationshipRepository()
    run = _create_run(module_id="nvc_analysis", workflow_run_id="wf-r1")
    with get_session() as session:
        constructs.replace_for_module_run(
            session,
            run,
            [
                Construct(
                    id="C001",
                    type="emotion",
                    label="Fear",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                ),
                Construct(
                    id="C002",
                    type="need",
                    label="Safety",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q002"],
                ),
            ],
        )
        relationships.replace_for_module_run(
            session,
            run,
            [
                ConstructRelationship(
                    id="R001",
                    source_construct_id="C001",
                    target_construct_id="C002",
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    confidence=Confidence.MODERATE,
                ),
                ConstructRelationship(
                    id="R002",
                    source_construct_id="C001",
                    target_construct_id="MISSING",
                    relationship_type=RelationshipType.SUPPORTS,
                    confidence=Confidence.LOW,
                ),
            ],
        )
        listed = relationships.list_by_workflow_run_id(session, "wf-r1")
        assert len(listed) == 2
        by_id = {item["source_id"]: item for item in listed}
        assert by_id["R001"]["ontology_resolved"] is True
        assert by_id["R001"]["source_construct_row_id"]
        assert by_id["R001"]["target_construct_row_id"]
        assert by_id["R001"]["link_warning"] is None
        assert by_id["R002"]["link_warning"]
        assert "MISSING" in by_id["R002"]["link_warning"]


def test_module_runner_persists_relationships_and_graph_edges() -> None:
    run = _create_run(module_id="gottman_analysis", workflow_run_id="wf-r2")
    output = ModuleRunOutput(
        module_id="gottman_analysis",
        module_version="1.0.0",
        executive_summary="Summary",
        findings=[],
        constructs=[
            Construct(
                id="C001",
                type="emotion",
                label="Anger",
                confidence=Confidence.HIGH,
                evidence_quote_ids=["Q001"],
            ),
            Construct(
                id="C002",
                type="interaction_cycle",
                label="Pursue-withdraw",
                confidence=Confidence.MODERATE,
                evidence_quote_ids=["Q002"],
            ),
        ],
        relationships=[
            ConstructRelationship(
                id="R001",
                source_construct_id="C001",
                target_construct_id="C002",
                relationship_type=RelationshipType.ESCALATES,
                confidence=Confidence.MODERATE,
            )
        ],
    )
    ModuleRunner()._complete_run(run, output, safety_flags=[])
    graph = ExplorationService().get_knowledge_graph("wf-r2")
    assert graph["source"] == "normalized"
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["relationship_type"] == "escalates"
