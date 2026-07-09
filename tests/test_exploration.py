import json
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import SourceType, WorkflowRunStatus
from backend.main import app
from backend.services.exploration_service import ExplorationService
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_engine import WorkflowEngine

FIXTURES = Path(__file__).parent / "fixtures"


def _module_llm_response(module_id: str) -> str:
    registry = ModuleRegistry()
    module = registry.get(module_id)
    if module_id == "meta_synthesis":
        payload = json.loads(
            (FIXTURES / "sample_synthesis_output.json").read_text(encoding="utf-8")
        )
    else:
        payload = json.loads(
            (FIXTURES / "sample_module_output.json").read_text(encoding="utf-8")
        )
    payload["module_id"] = module_id
    payload["module_version"] = module.config.version
    return f"```json\n{json.dumps(payload)}\n```"


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


def _ingest_golden(transcripts: TranscriptService):
    return transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Golden transcript",
    )


def _run_quick_review(mock_llm) -> tuple[WorkflowEngine, str]:
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)
    workflow_run = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    return engine, workflow_run.id


def test_exploration_finding_drilldown_includes_evidence_chain() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine, run_id = _run_quick_review(mock_llm)
    service = ExplorationService(workflows=engine, transcripts=TranscriptService())

    findings = service.list_findings(run_id)
    assert findings
    target_key = findings[0]["finding_key"]

    drilldown = service.get_finding_drilldown(run_id, target_key)
    assert drilldown["finding_key"] == target_key
    assert drilldown["evidence_chain"]
    assert drilldown["evidence_chain"][0]["quote_id"]


def test_exploration_cross_module_alignment_detects_shared_evidence() -> None:
    mock_llm = MagicMock()
    nvc_payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    nvc_module = ModuleRegistry().get("nvc_analysis")
    nvc_payload["module_id"] = "nvc_analysis"
    nvc_payload["module_version"] = nvc_module.config.version
    nvc_payload["findings"][0]["evidence_quote_ids"] = ["Q001"]
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        f"```json\n{json.dumps(nvc_payload)}\n```",
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine, run_id = _run_quick_review(mock_llm)
    service = ExplorationService(workflows=engine, transcripts=TranscriptService())

    alignment = service.get_cross_module_alignment(run_id)
    assert alignment["agreements"]


def test_exploration_knowledge_graph_builds_nodes_and_edges() -> None:
    module_run = MagicMock()
    module_run.status = "completed"
    module_run.module_id = "relationship_conversation_analysis"
    module_run.parsed_output = {
        "module_id": "relationship_conversation_analysis",
        "constructs": [
            {
                "id": "C001",
                "type": "need",
                "label": "Being heard",
                "confidence": "moderate",
                "evidence_quote_ids": ["Q001"],
            },
            {
                "id": "C002",
                "type": "emotion",
                "label": "Frustration",
                "confidence": "moderate",
                "evidence_quote_ids": ["Q002"],
            },
        ],
        "relationships": [
            {
                "id": "R001",
                "source_construct_id": "C001",
                "target_construct_id": "C002",
                "relationship_type": "reinforces",
                "confidence": "low",
            }
        ],
    }
    mock_workflows = MagicMock()
    mock_workflows.get_with_module_runs.return_value = (MagicMock(), [module_run])
    service = ExplorationService(workflows=mock_workflows)

    graph = service.get_knowledge_graph("run-1")
    assert len(graph["nodes"]) == 2
    assert graph["edges"]


def test_exploration_compare_workflow_runs() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)
    run_a = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    run_b = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    service = ExplorationService(workflows=engine, transcripts=TranscriptService())

    comparison = service.compare_workflow_runs([run_a.id, run_b.id])
    assert len(comparison["runs"]) == 2
    assert comparison["shared_themes"]


def test_exploration_ask_followup_uses_llm() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        "Because Q001 shows Person A stating they feel unheard.",
    ]
    engine, run_id = _run_quick_review(mock_llm)
    service = ExplorationService(workflows=engine, transcripts=TranscriptService(), llm=mock_llm)

    response = service.ask_followup(
        run_id,
        "Why was repair identified?",
        model="test-model",
    )
    assert "Q001" in response["answer"]
    assert response["context_scope"] == "workflow_run"


def test_exploration_api_endpoints(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        "Scoped answer citing Q001.",
    ]
    from backend.services.exploration_service import exploration_service
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(registry=ModuleRegistry(), llm=mock_llm, transcripts=TranscriptService())
    monkeypatch.setattr(workflow_engine, "_runner", runner)
    monkeypatch.setattr(exploration_service, "_llm", mock_llm)

    client = TestClient(app)
    transcript_response = client.post(
        "/api/transcripts",
        json={
            "raw_text": (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
            "source_type": "paste",
        },
    )
    transcript_id = transcript_response.json()["transcript"]["id"]

    run_response = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": transcript_id, "model": "test-model"},
    )
    run_id = run_response.json()["id"]
    assert run_response.json()["status"] == WorkflowRunStatus.COMPLETED.value

    findings_response = client.get(f"/api/workflow-runs/{run_id}/exploration/findings")
    assert findings_response.status_code == 200
    finding_key = findings_response.json()["findings"][0]["finding_key"]

    drilldown_response = client.get(
        f"/api/workflow-runs/{run_id}/exploration/findings/{finding_key}"
    )
    assert drilldown_response.status_code == 200
    assert drilldown_response.json()["evidence_chain"]

    cross_module_response = client.get(f"/api/workflow-runs/{run_id}/exploration/cross-module")
    assert cross_module_response.status_code == 200

    ask_response = client.post(
        f"/api/workflow-runs/{run_id}/exploration/ask",
        json={"question": "Why?", "model": "test-model"},
    )
    assert ask_response.status_code == 200
    assert ask_response.json()["answer"]

    transcript_runs_response = client.get(f"/api/transcripts/{transcript_id}/workflow-runs")
    assert transcript_runs_response.status_code == 200
    assert len(transcript_runs_response.json()["workflow_runs"]) == 1
