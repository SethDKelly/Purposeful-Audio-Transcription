"""Module output contracts against golden fixtures with mocked LLM responses."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import SourceType
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import transcript_service
from tests.helpers.golden_transcripts import (
    cites_any,
    contains_signal,
    forbidden_terms_in_output,
    validate_evidence_quote_ids,
)
from tests.test_workflow_engine import _module_llm_response

pytestmark = [pytest.mark.golden]


def _parse_module_response(module_id: str) -> dict:
    raw = _module_llm_response(module_id)
    payload = raw.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
    return json.loads(payload)


def _ingest_and_index(golden_fixture):
    bundle = transcript_service.ingest(
        raw_text=golden_fixture.labeled_text(),
        source_type=SourceType.PASTE,
        title=golden_fixture.fixture_id,
    )
    transcript_service.mark_ready(bundle.transcript.id, skip_review=True)
    quotes_by_id = {quote.quote_id: quote.text for quote in bundle.evidence_quotes}
    return bundle, quotes_by_id


@pytest.mark.parametrize(
    "module_id",
    [
        "relationship_conversation_analysis",
        "nvc_analysis",
        "bias_epistemic_quality",
    ],
)
def test_module_mock_output_cites_valid_quote_ids(golden_fixture, module_id) -> None:
    bundle, quotes_by_id = _ingest_and_index(golden_fixture)
    mock_llm = MagicMock()
    mock_llm.chat.return_value = _module_llm_response(module_id)

    runner = ModuleRunner(
        registry=ModuleRegistry(),
        llm=mock_llm,
        transcripts=transcript_service,
    )
    module_run = runner.run(
        module_id=module_id,
        transcript_id=bundle.transcript.id,
        model="mock",
    )
    assert module_run.status == "completed"
    output = module_run.parsed_output or {}
    validate_evidence_quote_ids(output, quotes_by_id.keys())

    findings = output.get("findings") or []
    assert findings
    assert all(finding.get("evidence_quote_ids") for finding in findings)


def test_mocked_relationship_module_detects_repair_signal(gt001_fixture) -> None:
    _, quotes_by_id = _ingest_and_index(gt001_fixture)
    output = _parse_module_response("relationship_conversation_analysis")

    assert contains_signal(output, "repair_attempt")
    signal = next(
        item
        for item in gt001_fixture.assertions["required_signals"]
        if item["id"] == "gt001_signal_005"
    )
    assert cites_any(output, signal["must_reference_any"], quotes_by_id=quotes_by_id)


def test_mock_output_avoids_forbidden_high_confidence_diagnosis(golden_fixture) -> None:
    output = _parse_module_response("bias_epistemic_quality")
    forbidden = golden_fixture.assertions.get("forbidden_or_low_confidence") or []
    assert not forbidden_terms_in_output(output, forbidden)
