"""Golden transcript fixture loading, quote IDs, assertions parse, mocked workflow smoke."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from fastapi.testclient import TestClient

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import SourceType
from backend.main import app
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import transcript_service
from backend.services.workflow_engine import WorkflowEngine, workflow_engine
from tests.helpers.golden_transcripts import iter_golden_fixtures
from tests.test_workflow_engine import _module_llm_response

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN_ROOT = FIXTURES / "golden_transcripts"


@pytest.fixture(params=iter_golden_fixtures(), ids=lambda g: g.path.name)
def golden(request) -> object:
    return request.param


def test_golden_fixture_dirs_exist() -> None:
    assert GOLDEN_ROOT.is_dir()
    names = {path.name for path in GOLDEN_ROOT.iterdir() if path.is_dir()}
    assert "GT001_missed_dinner_couple" in names
    assert "GT002_caregiving_siblings" in names


def test_load_transcript_json(golden) -> None:
    data = golden.transcript
    assert data.get("fixture_id")
    assert data.get("title")
    turns = data.get("turns") or []
    assert len(turns) >= 2
    for turn in turns:
        assert turn.get("turn_id")
        assert turn.get("speaker")
        assert (turn.get("text") or "").strip()


def test_metadata_and_assertions_parse(golden) -> None:
    meta = golden.metadata
    assertions = golden.assertions
    assert meta["fixture_id"] == golden.fixture_id
    assert assertions["fixture_id"] == golden.fixture_id
    structural = assertions.get("structural") or {}
    assert int(structural.get("min_turns") or 0) >= 1
    # Round-trip YAML remains a mapping after load.
    assert isinstance(yaml.safe_load(yaml.safe_dump(assertions)), dict)


def test_ingest_assigns_sequential_quote_ids(golden) -> None:
    assertions = golden.assertions.get("quote_ids") or {}
    text = golden.labeled_text()
    for phrase in (golden.assertions.get("must_contain_phrases") or []):
        assert phrase.lower() in text.lower()

    bundle = transcript_service.ingest(
        raw_text=text,
        source_type=SourceType.PASTE,
        title=golden.metadata.get("title") or golden.fixture_id,
    )
    quotes = bundle.evidence_quotes
    min_count = int(assertions.get("min_quote_count") or 1)
    assert len(quotes) >= min_count
    if assertions.get("require_sequential", True):
        for index, quote in enumerate(quotes, start=1):
            assert quote.quote_id == f"Q{index:03d}"
            assert quote.quote_index == index

    structural = golden.assertions.get("structural") or {}
    speakers = {s.display_name or s.label for s in bundle.speakers}
    for name in structural.get("participant_names") or []:
        assert name in speakers
    assert len(bundle.speakers) >= int(structural.get("min_speakers") or 1)


def test_mocked_quick_review_smoke_on_golden(golden, monkeypatch) -> None:
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
        raw_text=golden.labeled_text(),
        source_type=SourceType.PASTE,
        title=golden.fixture_id,
    )
    transcript_service.mark_ready(bundle.transcript.id, skip_review=True)

    engine = WorkflowEngine(runner=runner, transcripts=transcript_service)
    run = engine.run("quick_review", bundle.transcript.id, model="mock")
    assert run.status == "completed"
    assert mock_llm.chat.call_count >= 3


@pytest.mark.integration
@pytest.mark.golden
@pytest.mark.skipif(
    os.environ.get("RUN_GOLDEN_LIVE", "").strip().lower() not in {"1", "true", "yes"},
    reason="Set RUN_GOLDEN_LIVE=1 to run live Bedrock golden checks",
)
def test_live_golden_placeholder(golden) -> None:
    """Optional live-model golden harness — enable explicitly outside default CI."""
    client = TestClient(app)
    created = client.post(
        "/api/transcripts",
        json={
            "raw_text": golden.labeled_text(),
            "source_type": "paste",
            "title": golden.fixture_id,
        },
    )
    assert created.status_code == 200
    transcript_id = created.json()["transcript"]["id"]
    ready = client.post(
        f"/api/transcripts/{transcript_id}/ready",
        json={"skip_review": True},
    )
    assert ready.status_code == 200
    # Live path: operators run workflows against AWS; this placeholder only proves
    # the fixture can be ingested + marked ready under integration selection.
    assert ready.json()["transcript"]["analysis_ready"] is True
