"""Workflow smoke tests on golden fixtures (mocked by default)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import SourceType
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import transcript_service
from backend.services.workflow_engine import WorkflowEngine, workflow_engine
from tests.test_workflow_engine import _module_llm_response

pytestmark = [
    pytest.mark.golden,
    pytest.mark.integration,
]


def test_mocked_quick_review_smoke_on_golden(golden_fixture, monkeypatch) -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("meta_synthesis"),
    ]

    runner = ModuleRunner(
        registry=ModuleRegistry(), llm=mock_llm, transcripts=transcript_service
    )
    monkeypatch.setattr(workflow_engine, "_runner", runner)

    bundle = transcript_service.ingest(
        raw_text=golden_fixture.labeled_text(),
        source_type=SourceType.PASTE,
        title=golden_fixture.fixture_id,
    )
    transcript_service.mark_ready(bundle.transcript.id, skip_review=True)

    engine = WorkflowEngine(runner=runner, transcripts=transcript_service)
    run = engine.run("quick_review", bundle.transcript.id, model="mock")
    assert run.status == "completed"
    assert mock_llm.chat.call_count >= 3


def _live_golden_enabled() -> bool:
    flag = os.environ.get("RUN_LIVE_GOLDEN_TESTS") or os.environ.get("RUN_GOLDEN_LIVE", "")
    return flag.strip().lower() in {"1", "true", "yes"}


@pytest.mark.live_model
@pytest.mark.slow
@pytest.mark.skipif(
    not _live_golden_enabled(),
    reason="Set RUN_LIVE_GOLDEN_TESTS=1 (or RUN_GOLDEN_LIVE=1) for live golden checks",
)
def test_live_golden_ingest_and_ready(golden_fixture) -> None:
    """Optional live-model golden harness — proves fixture ingest + ready path."""
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": golden_fixture.labeled_text(),
            "source_type": "paste",
            "title": golden_fixture.fixture_id,
        },
    )
    assert created.status_code == 200
    transcript_id = created.json()["transcript"]["id"]
    ready = client.post(
        f"/api/transcripts/{transcript_id}/ready",
        json={"skip_review": True},
    )
    assert ready.status_code == 200
    assert ready.json()["transcript"]["analysis_ready"] is True
