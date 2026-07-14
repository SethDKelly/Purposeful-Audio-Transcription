import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import ModuleRunStatus, SourceType, WorkflowRunStatus
from backend.main import app
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
    ceiling = module.config.confidence_ceiling.value
    for finding in payload.get("findings", []):
        conf = finding.get("confidence")
        if conf not in {"observed", "insufficient_evidence"} and conf != ceiling:
            # Keep fixtures valid across modules with lower ceilings (e.g. trauma = low).
            if conf in {"high", "moderate", "low", "exploratory"}:
                finding["confidence"] = ceiling
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


def test_workflow_engine_quick_review() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)

    workflow_run = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    _, module_runs = engine.get_with_module_runs(workflow_run.id)

    assert workflow_run.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 3
    assert all(run.status == ModuleRunStatus.COMPLETED.value for run in module_runs)
    assert all(run.workflow_run_id == workflow_run.id for run in module_runs)
    assert mock_llm.chat.call_count == 3


def test_workflow_engine_full_mvp_runs_synthesis_last() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("systems_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("meta_synthesis"),
    ]
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)

    workflow_run = engine.run(
        workflow_id="full_mvp",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    _, module_runs = engine.get_with_module_runs(workflow_run.id)

    assert workflow_run.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 5
    assert module_runs[-1].module_id == "meta_synthesis"
    assert module_runs[-1].parsed_output is not None

    synthesis_user_message = mock_llm.chat.call_args_list[-1][0][1][1]["content"]
    assert "Prior Module Outputs" in synthesis_user_message
    assert "relationship_conversation_analysis" in synthesis_user_message
    assert "Evidence Index" not in synthesis_user_message


def test_workflow_engine_fails_when_module_fails() -> None:
    mock_llm = MagicMock()
    bad_payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    bad_payload["findings"][0]["evidence_quote_ids"] = ["Q999"]
    mock_llm.chat.return_value = f"```json\n{json.dumps(bad_payload)}\n```"
    engine = _build_engine(mock_llm)
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)

    workflow_run = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    assert workflow_run.status == WorkflowRunStatus.FAILED.value
    assert workflow_run.error_log


def test_workflows_api(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(registry=ModuleRegistry(), llm=mock_llm, transcripts=TranscriptService())
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    client = TestClient(app)
    list_response = client.get("/api/workflows")
    assert list_response.status_code == 200
    assert len(list_response.json()["workflows"]) == 7

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
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["status"] == WorkflowRunStatus.COMPLETED.value
    assert len(payload["module_runs"]) == 3

    get_response = client.get(f"/api/workflow-runs/{payload['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["workflow_id"] == "quick_review"
