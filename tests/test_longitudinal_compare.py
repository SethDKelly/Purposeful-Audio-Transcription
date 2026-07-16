"""Longitudinal case comparison (v0.9 P3)."""

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.domain.enums import Confidence, FindingType, ModuleRunStatus, SourceType
from backend.domain.finding import Finding
from backend.main import app
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.repositories.workflow_run_repository import WorkflowRunRepository
from backend.services.case_service import case_service
from backend.services.transcript_service import TranscriptService


def test_compare_case_transcripts() -> None:
    client = TestClient(app)
    case = case_service.create(title="Longitudinal case")
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

    # Seed completed workflow runs with findings via repositories + mark workflow completed
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
                ),
                Finding(
                    id="F002",
                    module_run_id=run2.id,
                    type=FindingType.OBSERVATION,
                    title="Repair attempt",
                    summary="New repair",
                    confidence=Confidence.HIGH,
                    evidence_quote_ids=["Q002"],
                ),
            ],
        )

    response = client.post(
        "/api/exploration/compare-transcripts",
        json={"case_id": case.id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["transcripts"] == 2
    assert payload["counts"]["shared_themes"] >= 1
    assert payload["counts"]["new_themes"] >= 1
