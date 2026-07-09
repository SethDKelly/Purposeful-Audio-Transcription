import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.core.exceptions import ModuleRunError
from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import ModuleRunStatus, SourceType
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService

FIXTURES = Path(__file__).parent / "fixtures"


def _valid_llm_response() -> str:
    payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    return f"```json\n{json.dumps(payload)}\n```\n\n## Report"


def _build_runner(mock_llm) -> ModuleRunner:
    return ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=TranscriptService(),
    )


def test_module_runner_completes_with_valid_output() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.return_value = _valid_llm_response()
    runner = _build_runner(mock_llm)

    bundle = runner._transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
        title="Golden transcript",
    )

    run = runner.run(
        module_id="relationship_conversation_analysis",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    assert run.status == ModuleRunStatus.COMPLETED.value
    assert run.parsed_output is not None
    assert len(run.parsed_output["findings"]) == 3
    assert run.model_used == "test-model"
    mock_llm.chat.assert_called_once()


def test_module_runner_retries_then_succeeds() -> None:
    mock_llm = MagicMock()
    bad_payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    bad_payload["findings"][2]["alternative_explanations"] = []
    mock_llm.chat.side_effect = [
        f"```json\n{json.dumps(bad_payload)}\n```",
        _valid_llm_response(),
    ]
    runner = _build_runner(mock_llm)

    bundle = runner._transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
    )

    run = runner.run(
        module_id="relationship_conversation_analysis",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    assert run.status == ModuleRunStatus.COMPLETED.value
    assert mock_llm.chat.call_count == 2


def test_module_runner_fails_after_retries() -> None:
    mock_llm = MagicMock()
    bad_payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    bad_payload["findings"][2]["alternative_explanations"] = []
    mock_llm.chat.return_value = f"```json\n{json.dumps(bad_payload)}\n```"
    runner = _build_runner(mock_llm)

    bundle = runner._transcripts.ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
    )

    run = runner.run(
        module_id="relationship_conversation_analysis",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    assert run.status == ModuleRunStatus.FAILED.value
    assert run.validation_errors
    assert mock_llm.chat.call_count == 3


def test_module_runner_rejects_meta_synthesis_direct_run() -> None:
    mock_llm = MagicMock()
    runner = _build_runner(mock_llm)
    bundle = runner._transcripts.ingest("Person A: Hello.", source_type=SourceType.PASTE)

    with pytest.raises(ModuleRunError, match="prior module outputs"):
        runner.run(
            module_id="meta_synthesis",
            transcript_id=bundle.transcript.id,
            model="test-model",
        )

    mock_llm.chat.assert_not_called()


@pytest.mark.parametrize(
    "module_id",
    [
        "relationship_conversation_analysis",
        "nvc_analysis",
        "systems_analysis",
        "bias_epistemic_quality",
    ],
)
def test_module_runner_supports_transcript_modules(module_id: str) -> None:
    mock_llm = MagicMock()
    payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    payload["module_id"] = module_id
    registry = ModuleRegistry()
    payload["module_version"] = registry.get(module_id).config.version
    mock_llm.chat.return_value = f"```json\n{json.dumps(payload)}\n```"
    runner = _build_runner(mock_llm)

    bundle = runner._transcripts.ingest(
        (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
        source_type=SourceType.PASTE,
    )

    run = runner.run(
        module_id=module_id,
        transcript_id=bundle.transcript.id,
        model="test-model",
    )

    assert run.status == ModuleRunStatus.COMPLETED.value
    assert run.parsed_output["module_id"] == module_id


def test_run_module_api_with_mock(monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.return_value = _valid_llm_response()
    from backend.services.module_runner import module_runner

    monkeypatch.setattr(module_runner, "_llm", mock_llm)

    client = TestClient(app)
    transcript_response = client.post(
        "/api/transcripts",
        json={
            "raw_text": (FIXTURES / "golden_transcript.txt").read_text(encoding="utf-8"),
            "source_type": "paste",
            "title": "Golden transcript",
        },
    )
    transcript_id = transcript_response.json()["transcript"]["id"]

    run_response = client.post(
        "/api/modules/relationship_conversation_analysis/run",
        json={"transcript_id": transcript_id, "model": "test-model"},
    )
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["status"] == ModuleRunStatus.COMPLETED.value
    assert payload["parsed_output"]["findings"]

    get_response = client.get(f"/api/module-runs/{payload['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == payload["id"]
