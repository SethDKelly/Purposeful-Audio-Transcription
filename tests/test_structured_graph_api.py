"""Structured graph inventory API (v0.8 P6)."""

from fastapi.testclient import TestClient

from backend.db.base import get_session
from backend.domain.enums import Confidence, ModuleRunStatus, SourceType
from backend.domain.finding import Construct, Finding
from backend.domain.enums import FindingType
from backend.main import app
from backend.repositories.construct_repository import ConstructRepository
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.services.transcript_service import TranscriptService


def test_structured_graph_endpoint() -> None:
    client = TestClient(app)
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="structured-api",
    )
    with get_session() as session:
        run = ModuleRunRepository().create(
            session,
            module_id="nvc_analysis",
            transcript_id=bundle.transcript.id,
            workflow_run_id="wf-struct",
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
                    title="Hello exchange",
                    summary="Greeting observed.",
                    confidence=Confidence.HIGH,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )
        ConstructRepository().replace_for_module_run(
            session,
            run,
            [
                Construct(
                    id="C001",
                    type="emotion",
                    label="Warmth",
                    confidence=Confidence.MODERATE,
                    evidence_quote_ids=["Q001"],
                )
            ],
        )

    response = client.get("/api/workflow-runs/wf-struct/structured-graph")
    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["findings"] == 1
    assert payload["counts"]["constructs"] == 1
    assert payload["findings"][0]["title"] == "Hello exchange"
    assert payload["constructs"][0]["label"] == "Warmth"
