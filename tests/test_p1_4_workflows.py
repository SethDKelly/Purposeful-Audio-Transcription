"""P1-4 workflow completeness — full multidisciplinary + research suites."""

from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import ModuleRunStatus, SourceType, WorkflowRunStatus
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_engine import WorkflowEngine
from config.settings import settings
from tests.test_workflow_engine import _module_llm_response

FIXTURES = Path(__file__).parent / "fixtures"

_FULL_MODULES = [
    "relationship_conversation_analysis",
    "nvc_analysis",
    "gottman_analysis",
    "attachment_interaction_matrix",
    "emotional_needs_values",
    "cognitive_analysis",
    "narrative_identity_analysis",
    "trauma_informed_communication",
    "exploratory_psychological_formulation",
    "mediation_analysis",
    "systems_analysis",
    "bias_epistemic_quality",
    "meta_synthesis",
]

_RESEARCH_MODULES = [
    "relationship_conversation_analysis",
    "cognitive_analysis",
    "narrative_identity_analysis",
    "bias_epistemic_quality",
    "systems_analysis",
    "meta_synthesis",
]


def _build_engine(mock_llm) -> WorkflowEngine:
    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )
    return WorkflowEngine(
        workflows=WorkflowRegistry(),
        runner=runner,
        transcripts=TranscriptService(),
    )


def _ingest_golden() -> str:
    bundle = TranscriptService().ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Golden transcript",
    )
    return bundle.transcript.id


def test_workflow_defs_include_new_suites() -> None:
    registry = WorkflowRegistry()
    full = registry.get("full_multidisciplinary")
    research = registry.get("research_oriented")
    assert full.config.default_background is True
    assert research.config.default_background is True
    assert full.module_sequence == _FULL_MODULES
    assert research.module_sequence == _RESEARCH_MODULES
    assert len(full.module_sequence) == 13
    assert full.module_sequence[-1] == "meta_synthesis"


def test_research_oriented_engine_completes() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [_module_llm_response(mid) for mid in _RESEARCH_MODULES]
    engine = _build_engine(mock_llm)
    transcript_id = _ingest_golden()

    workflow_run = engine.run(
        workflow_id="research_oriented",
        transcript_id=transcript_id,
        model="test-model",
    )
    _, module_runs = engine.get_with_module_runs(workflow_run.id)

    assert workflow_run.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 6
    assert [run.module_id for run in module_runs] == _RESEARCH_MODULES
    assert all(run.status == ModuleRunStatus.COMPLETED.value for run in module_runs)
    assert module_runs[-1].module_id == "meta_synthesis"


def test_full_multidisciplinary_engine_completes() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [_module_llm_response(mid) for mid in _FULL_MODULES]
    engine = _build_engine(mock_llm)
    transcript_id = _ingest_golden()

    workflow_run = engine.run(
        workflow_id="full_multidisciplinary",
        transcript_id=transcript_id,
        model="test-model",
    )
    _, module_runs = engine.get_with_module_runs(workflow_run.id)

    assert workflow_run.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 13
    assert [run.module_id for run in module_runs] == _FULL_MODULES
    assert all(run.status == ModuleRunStatus.COMPLETED.value for run in module_runs)


def test_full_multidisciplinary_rejects_explicit_sync(monkeypatch) -> None:
    monkeypatch.setattr(settings, "workflow_sync_module_limit", 6)
    client = TestClient(app)
    transcript_id = client.post(
        "/api/transcripts",
        json={
            "raw_text": (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
            "source_type": "paste",
        },
    ).json()["transcript"]["id"]

    response = client.post(
        "/api/workflows/full_multidisciplinary/run",
        json={
            "transcript_id": transcript_id,
            "model": "test-model",
            "background": False,
        },
    )
    assert response.status_code == 400
    assert "synchronous" in response.json()["detail"].lower()


def test_full_multidisciplinary_defaults_to_background(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [_module_llm_response(mid) for mid in _FULL_MODULES]
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(
        registry=ModuleRegistry(), llm=mock_llm, transcripts=TranscriptService()
    )
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    client = TestClient(app)
    list_response = client.get("/api/workflows")
    ids = {item["id"] for item in list_response.json()["workflows"]}
    assert "full_multidisciplinary" in ids
    assert "research_oriented" in ids

    transcript_id = client.post(
        "/api/transcripts",
        json={
            "raw_text": (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
            "source_type": "paste",
        },
    ).json()["transcript"]["id"]

    run_response = client.post(
        "/api/workflows/full_multidisciplinary/run",
        json={"transcript_id": transcript_id, "model": "test-model"},
    )
    assert run_response.status_code == 200
    run_id = run_response.json()["id"]

    final_status = None
    for _ in range(200):
        status_response = client.get(f"/api/workflow-runs/{run_id}")
        final_status = status_response.json()["status"]
        if final_status in {
            WorkflowRunStatus.COMPLETED.value,
            WorkflowRunStatus.FAILED.value,
        }:
            break
    assert final_status == WorkflowRunStatus.COMPLETED.value
    payload = client.get(f"/api/workflow-runs/{run_id}").json()
    assert len(payload["module_runs"]) == 13
