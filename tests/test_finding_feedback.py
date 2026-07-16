"""Finding feedback API (v0.9 P6)."""

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.domain.enums import Confidence, FindingType, ModuleRunStatus, SourceType
from backend.domain.finding import Finding
from backend.main import app
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.services.transcript_service import TranscriptService
from urllib.parse import quote


def test_submit_finding_feedback() -> None:
    client = TestClient(app)
    bundle = TranscriptService().ingest(
        "Person A: Hi.\nPerson B: Hello.",
        source_type=SourceType.PASTE,
        title="feedback",
    )
    with get_session() as session:
        run = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-feedback",
        )
        run.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run)
        FindingRepository().replace_for_module_run(
            session,
            run,
            [
                Finding(
                    id="F001",
                    module_run_id=run.id,
                    type=FindingType.OBSERVATION,
                    title="Theme",
                    summary="Summary",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )

    key = quote("nvc_analysis:F001", safe="")
    response = client.post(
        f"/api/workflow-runs/wf-feedback/findings/{key}/feedback",
        json={"rating": "helpful", "note": "Useful", "transcript_id": bundle.transcript.id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["rating"] == "helpful"
    assert payload["finding_row_id"]

    listed = client.get("/api/workflow-runs/wf-feedback/feedback")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
