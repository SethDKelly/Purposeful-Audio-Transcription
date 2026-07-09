import json
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import SourceType, WorkflowRunStatus
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.synthesis_engine import SynthesisEngine
from backend.services.synthesis_parser import SynthesisParser
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
        payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    payload["module_id"] = module_id
    payload["module_version"] = module.config.version
    return f"```json\n{json.dumps(payload)}\n```"


def _run_quick_review_workflow(mock_llm):
    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )
    engine = WorkflowEngine(
        workflows=WorkflowRegistry(),
        runner=runner,
        transcripts=TranscriptService(),
    )
    bundle = TranscriptService().ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
    )
    workflow_run = engine.run(
        workflow_id="quick_review",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    return workflow_run, engine


def test_synthesis_parser_accepts_synthesis_output_shape() -> None:
    payload = json.loads(
        (FIXTURES / "sample_synthesis_report.json").read_text(encoding="utf-8")
    )
    parser = SynthesisParser()
    from backend.services.synthesis_preprocessor import SynthesisPreprocessor

    preprocessed = SynthesisPreprocessor().process([])
    report = parser.parse_meta_module_output(
        payload,
        workflow_run_id="wf-1",
        synthesis_id="syn-1",
        module_run_id="meta-run-1",
        preprocessed=preprocessed,
    )

    assert report.convergence
    assert report.divergence
    assert report.moderate_confidence_findings


def test_synthesis_engine_builds_quick_review_report() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]
    workflow_run, workflow_engine = _run_quick_review_workflow(mock_llm)

    synthesis_engine = SynthesisEngine(workflows=workflow_engine)
    report = synthesis_engine.get_report(workflow_run.id)

    assert report.executive_summary
    assert report.convergence or report.divergence or report.high_confidence_findings
    assert report.interventions
    assert len(report.source_module_run_ids) == 3

    cached = synthesis_engine.get_report(workflow_run.id)
    assert cached.id == report.id


def test_synthesis_engine_full_mvp_includes_meta_synthesis_sections() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("systems_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("meta_synthesis"),
    ]
    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )
    workflow_engine = WorkflowEngine(
        workflows=WorkflowRegistry(),
        runner=runner,
        transcripts=TranscriptService(),
    )
    bundle = TranscriptService().ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
    )
    workflow_run = workflow_engine.run(
        workflow_id="full_mvp",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    synthesis_engine = SynthesisEngine(workflows=workflow_engine)
    report = synthesis_engine.get_report(workflow_run.id)

    assert report.convergence
    assert report.executive_summary
    assert report.interventions
    assert len(report.source_module_run_ids) == 5


def test_synthesis_api(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
    ]

    from backend.services.workflow_engine import workflow_engine as wf_engine

    runner = ModuleRunner(registry=ModuleRegistry(), llm=mock_llm, transcripts=TranscriptService())
    monkeypatch.setattr(wf_engine, "_runner", runner)

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
    workflow_run_id = run_response.json()["id"]
    assert run_response.json()["status"] == WorkflowRunStatus.COMPLETED.value

    synthesis_response = client.get(f"/api/workflow-runs/{workflow_run_id}/synthesis")
    assert synthesis_response.status_code == 200
    payload = synthesis_response.json()
    assert payload["workflow_run_id"] == workflow_run_id
    assert payload["executive_summary"]
