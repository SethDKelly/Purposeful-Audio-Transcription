"""Tests for safety-aware report mode (v1.0 P5)."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.domain.enums import SourceType
from backend.main import app
from backend.services.safety_risk_scanner import (
    SKIP_IN_SAFETY_MODE,
    safety_risk_scanner,
)
from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import workflow_registry
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService
from backend.services.workflow_engine import WorkflowEngine
from tests.test_workflow_engine import (
    _ingest_golden,
    _module_llm_response,
)


def test_safety_scanner_detects_high_risk() -> None:
    result = safety_risk_scanner.scan(
        "Person A: I will kill you if you leave.\nPerson B: Please stop."
    )
    assert result.risk_level == "high"
    assert "threats" in result.matched_categories
    assert result.safety_mode_recommended is True


def test_safety_scanner_none_for_benign_text() -> None:
    result = safety_risk_scanner.scan("Person A: Thanks for meeting today.")
    assert result.risk_level == "none"
    assert result.matched_categories == []


def test_safety_assessment_api() -> None:
    transcripts = TranscriptService()
    bundle = transcripts.ingest(
        "Person A: I want to die.\nPerson B: Are you okay?",
        source_type=SourceType.PASTE,
        title="Safety scan",
    )
    client = TestClient(app)
    response = client.get(f"/api/transcripts/{bundle.transcript.id}/safety-assessment")
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "high"
    assert body["safety_mode_recommended"] is True


def test_safety_mode_skips_exploratory_modules(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("meta_synthesis"),
    ]
    engine: WorkflowEngine = WorkflowEngine(
        workflows=workflow_registry,
        runner=ModuleRunner(
            registry=ModuleRegistry(),
            llm=mock_llm,
            transcripts=TranscriptService(),
        ),
        transcripts=TranscriptService(),
    )
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)
    transcripts.mark_ready(bundle.transcript.id)

    from backend.services.custom_workflow_service import custom_workflow_service

    modules = [
        "relationship_conversation_analysis",
        "nvc_analysis",
        *sorted(SKIP_IN_SAFETY_MODE),
        "meta_synthesis",
    ]
    _, workflow_id = custom_workflow_service.build_definition(
        modules=modules,
        safety_mode=True,
    )
    run = engine.run(
        workflow_id=workflow_id,
        transcript_id=bundle.transcript.id,
        model="test-model",
        safety_mode=True,
    )
    _, module_runs = engine.get_with_module_runs(run.id)
    executed = {module_run.module_id for module_run in module_runs}
    assert SKIP_IN_SAFETY_MODE.isdisjoint(executed)
    assert run.safety_mode is True


def test_safety_mode_adds_synthesis_framing() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("systems_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("meta_synthesis"),
    ]
    engine = WorkflowEngine(
        workflows=workflow_registry,
        runner=ModuleRunner(
            registry=ModuleRegistry(),
            llm=mock_llm,
            transcripts=TranscriptService(),
        ),
        transcripts=TranscriptService(),
    )
    transcripts = TranscriptService()
    bundle = _ingest_golden(transcripts)
    transcripts.mark_ready(bundle.transcript.id)

    engine.run(
        "full_mvp",
        bundle.transcript.id,
        model="test-model",
        safety_mode=True,
    )
    synthesis_message = mock_llm.chat.call_args_list[-1][0][1][1]["content"]
    assert "Safety-aware framing" in synthesis_message


def test_run_workflow_auto_enables_safety_mode_on_high_risk(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    from backend.services.workflow_engine import workflow_engine

    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    transcripts = TranscriptService()
    bundle = transcripts.ingest(
        "Person A: I will kill you.\nPerson B: Stop threatening me.",
        source_type=SourceType.PASTE,
        title="Threat transcript",
    )
    transcripts.mark_ready(bundle.transcript.id)

    client = TestClient(app)
    response = client.post(
        "/api/workflows/quick_review/run",
        json={"transcript_id": bundle.transcript.id, "model": "test-model"},
    )
    assert response.status_code == 200
    assert response.json()["safety_mode"] is True
