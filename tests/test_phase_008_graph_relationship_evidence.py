"""Phase 008 — graph relationship evidence and case correctness."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.db.base import get_session
from backend.db.models import (
    ConstructRelationshipEvidenceQuoteRow,
    ConstructRelationshipRow,
    ConstructRow,
)
from backend.domain.enums import Confidence, FindingType, ModuleRunStatus, RelationshipType, SourceType
from backend.domain.finding import Construct, ConstructRelationship, Finding
from backend.evaluation.harness import EvalGateConfig, evaluate_module_output
from backend.main import app
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.repositories.relationship_repository import ConstructRelationshipRepository
from backend.repositories.workflow_run_repository import WorkflowRunRepository
from backend.services.case_service import case_service
from backend.services.exploration_service import ExplorationService
from backend.services.graph_merge_service import GraphMergeService
from backend.services.module_output_validator import ModuleOutputValidator
from backend.services.output_parser import OutputParser
from backend.services.run_selection import select_latest_completed_run
from backend.services.transcript_service import TranscriptService
from sqlalchemy import select
from tests.helpers.golden_transcripts import load_golden_fixture_by_id


def test_parser_passes_relationship_evidence_fields() -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    output = parser.normalize(
        {
            "module_id": module.config.id,
            "module_version": module.config.version,
            "executive_summary": "Summary",
            "findings": [],
            "constructs": [
                {
                    "id": "C001",
                    "type": "emotion",
                    "label": "Fear",
                    "confidence": "moderate",
                    "evidence_quote_ids": ["Q001"],
                },
                {
                    "id": "C002",
                    "type": "need",
                    "label": "Safety",
                    "confidence": "moderate",
                    "evidence_quote_ids": ["Q002"],
                },
            ],
            "relationships": [
                {
                    "id": "R001",
                    "source_construct_id": "C001",
                    "target_construct_id": "C002",
                    "relationship_type": "contributes_to",
                    "confidence": "moderate",
                    "rationale": "Fear drives safety-seeking.",
                    "evidence_quote_ids": ["Q001"],
                    "alternative_explanations": ["Could be habit rather than fear."],
                }
            ],
        },
        module,
        "run-rel-1",
    )
    rel = output.relationships[0]
    assert rel.rationale == "Fear drives safety-seeking."
    assert rel.evidence_quote_ids == ["Q001"]
    assert rel.alternative_explanations == ["Could be habit rather than fear."]


def test_validator_warns_on_relationship_without_evidence_or_rationale() -> None:
    parser = OutputParser()
    registry = ModuleRegistry()
    module = registry.get("relationship_conversation_analysis")
    output = parser.normalize(
        {
            "module_id": module.config.id,
            "module_version": module.config.version,
            "executive_summary": "Summary",
            "findings": [],
            "constructs": [],
            "relationships": [
                {
                    "id": "R001",
                    "source_construct_id": "C001",
                    "target_construct_id": "C002",
                    "relationship_type": "supports",
                    "confidence": "moderate",
                }
            ],
        },
        module,
        "run-rel-2",
    )
    result = ModuleOutputValidator().validate(output, module, valid_quote_ids={"Q001"})
    assert result.is_valid
    assert any("no evidence_quote_ids and no rationale" in w for w in result.warnings)
    assert any("alternative_explanations" in w for w in result.warnings)


def test_relationship_persistence_writes_evidence_and_rationale() -> None:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="rel-evidence",
    )
    with get_session() as session:
        run = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-rel-ev",
        )
        run.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run)
        ConstructRepository().replace_for_module_run(
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
        ConstructRelationshipRepository().replace_for_module_run(
            session,
            run,
            [
                ConstructRelationship(
                    id="R001",
                    source_construct_id="C001",
                    target_construct_id="C002",
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    confidence=Confidence.MODERATE,
                    rationale="Linked by repeated turns.",
                    evidence_quote_ids=["Q001", "Q002"],
                    alternative_explanations=["Co-occurrence only."],
                )
            ],
        )
        listed = ConstructRelationshipRepository().list_by_workflow_run_id(
            session, "wf-rel-ev"
        )
        assert len(listed) == 1
        assert listed[0]["rationale"] == "Linked by repeated turns."
        assert listed[0]["evidence_quote_ids"] == ["Q001", "Q002"]
        assert listed[0]["alternative_explanations"] == ["Co-occurrence only."]
        quote_rows = session.scalars(
            select(ConstructRelationshipEvidenceQuoteRow).where(
                ConstructRelationshipEvidenceQuoteRow.relationship_id == listed[0]["row_id"]
            )
        ).all()
        assert {q.quote_id for q in quote_rows} == {"Q001", "Q002"}


def test_graph_merge_rewires_relationship_after_absorb() -> None:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="merge-rel",
    )
    constructs = ConstructRepository()
    relationships = ConstructRelationshipRepository()
    module_runs = ModuleRunRepository()
    with get_session() as session:
        run_a = module_runs.create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-merge-rel",
        )
        run_a.status = ModuleRunStatus.COMPLETED.value
        module_runs.save(session, run_a)
        run_b = module_runs.create(
            session,
            module_id="gottman_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-merge-rel",
        )
        run_b.status = ModuleRunStatus.COMPLETED.value
        module_runs.save(session, run_b)
        constructs.replace_for_module_run(
            session,
            run_a,
            [
                Construct(
                    id="C001",
                    type="emotion",
                    label="Defensiveness",
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
        constructs.replace_for_module_run(
            session,
            run_b,
            [
                Construct(
                    id="C010",
                    type="emotion",
                    label="defensive posture",
                    confidence=Confidence.HIGH,
                    evidence_quote_ids=["Q003"],
                )
            ],
        )
        relationships.replace_for_module_run(
            session,
            run_a,
            [
                ConstructRelationship(
                    id="R001",
                    source_construct_id="C001",
                    target_construct_id="C002",
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    confidence=Confidence.MODERATE,
                    rationale="Defensiveness blocks safety bids.",
                    evidence_quote_ids=["Q001"],
                )
            ],
        )

    result = GraphMergeService().merge_workflow_constructs("wf-merge-rel")
    assert result.constructs_absorbed == 1

    with get_session() as session:
        rels = session.scalars(
            select(ConstructRelationshipRow).where(
                ConstructRelationshipRow.workflow_run_id == "wf-merge-rel"
            )
        ).all()
        assert len(rels) == 1
        rel = rels[0]
        source = session.get(ConstructRow, rel.source_construct_row_id)
        assert source is not None
        assert source.is_canonical is True
        assert rel.source_construct_source_id == source.source_id

    graph = ExplorationService().get_knowledge_graph("wf-merge-rel")
    assert graph["source"] == "normalized"
    assert len(graph["edges"]) == 1
    edge = graph["edges"][0]
    assert edge["rationale"] == "Defensiveness blocks safety bids."
    assert edge["evidence_quote_ids"] == ["Q001"]
    node_ids = {n["id"] for n in graph["nodes"]}
    assert edge["source"] in node_ids
    assert edge["target"] in node_ids


def test_select_latest_completed_run_prefers_newer() -> None:
    runs = [
        {"id": "newer", "status": "completed"},
        {"id": "older", "status": "completed"},
    ]
    assert select_latest_completed_run(runs)["id"] == "newer"
    mixed = [
        {"id": "failed-new", "status": "failed"},
        {"id": "completed", "status": "completed"},
        {"id": "older", "status": "completed"},
    ]
    assert select_latest_completed_run(mixed)["id"] == "completed"
    assert select_latest_completed_run([{"id": "x", "status": "running"}]) is None


def test_duplicate_q001_across_transcripts_not_recurring_quote_collision() -> None:
    client = TestClient(app)
    case = case_service.create(title="Phase 008 case")
    t1 = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="Session 1",
    )
    t2 = TranscriptService().ingest(
        "Person A: Later.\nPerson B: Yes.",
        source_type=SourceType.PASTE,
        title="Session 2",
    )
    case_service.assign_transcript(t1.transcript.id, case_id=case.id, session_label="S1")
    case_service.assign_transcript(t2.transcript.id, case_id=case.id, session_label="S2")

    with get_session() as session:
        wr1 = WorkflowRunRepository().create(
            session,
            workflow_id="quick_review",
            transcript_id=t1.transcript.id,
            model_used="test",
        )
        wr1.status = "completed"
        WorkflowRunRepository().save(session, wr1)
        wr2 = WorkflowRunRepository().create(
            session,
            workflow_id="quick_review",
            transcript_id=t2.transcript.id,
            model_used="test",
        )
        wr2.status = "completed"
        WorkflowRunRepository().save(session, wr2)
        run1 = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=t1.transcript.id,
            workflow_run_id=wr1.id,
        )
        run1.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run1)
        FindingRepository().replace_for_module_run(
            session,
            run1,
            [
                Finding(
                    id="F001",
                    module_run_id=run1.id,
                    type=FindingType.OBSERVATION,
                    title="Defensiveness",
                    summary="Early defensiveness",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )
        run2 = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=t2.transcript.id,
            workflow_run_id=wr2.id,
        )
        run2.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run2)
        FindingRepository().replace_for_module_run(
            session,
            run2,
            [
                Finding(
                    id="F001",
                    module_run_id=run2.id,
                    type=FindingType.OBSERVATION,
                    title="Defensiveness",
                    summary="Still present",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )

    response = client.post(
        "/api/exploration/compare-transcripts",
        json={"case_id": case.id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recurring_evidence_quote_ids"] == []
    assert payload["recurring_evidence_refs"] == []
    assert payload["counts"]["shared_themes"] >= 1
    assert "recurring_theme_keys" in payload
    assert len(payload["sessions"]) == 2
    for session in payload["sessions"]:
        assert "transcript_version_id" in session
        refs = session["evidence_refs"]
        assert refs
        assert all(ref["quote_id"] == "Q001" for ref in refs)
        assert all(ref["transcript_id"] == session["transcript_id"] for ref in refs)
    # Same bare quote id across transcripts must remain distinct by transcript_id.
    tids = {ref["transcript_id"] for s in payload["sessions"] for ref in s["evidence_refs"]}
    assert tids == {t1.transcript.id, t2.transcript.id}


def test_eval_counts_relationship_without_evidence_or_rationale() -> None:
    fixture = load_golden_fixture_by_id("GT001")
    result = evaluate_module_output(
        fixture=fixture,
        module_id="relationship_conversation_analysis",
        module_output={
            "findings": [],
            "constructs": [],
            "relationships": [
                {
                    "source_construct_id": "C001",
                    "target_construct_id": "C002",
                    "relationship_type": "supports",
                    "confidence": "moderate",
                },
                {
                    "source_construct_id": "C001",
                    "target_construct_id": "C003",
                    "relationship_type": "escalates",
                    "confidence": "low",
                    "rationale": "Escalation turn.",
                    "evidence_quote_ids": ["Q001"],
                },
            ],
        },
        gates=EvalGateConfig(max_relationship_without_evidence_or_rationale=0),
    )
    assert result.relationship_without_evidence_or_rationale_count == 1
    assert result.gate_passed is False
