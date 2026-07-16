"""Tests for long transcript strategy and length assessment API (v1.0 P4)."""

import uuid

from fastapi.testclient import TestClient

from backend.domain.enums import SourceType
from backend.domain.transcript import EvidenceQuote
from backend.main import app
from backend.services.evidence_index import STRATEGY_BALANCED_SAMPLE, EvidenceIndexService
from backend.services.transcript_length_service import TranscriptLengthService
from backend.services.transcript_service import TranscriptService


def _make_quotes(count: int) -> list[EvidenceQuote]:
    speaker_id = str(uuid.uuid4())
    transcript_id = str(uuid.uuid4())
    return [
        EvidenceQuote(
            id=str(uuid.uuid4()),
            transcript_id=transcript_id,
            turn_id=str(uuid.uuid4()),
            speaker_id=speaker_id,
            quote_index=index,
            quote_id=f"Q{index:03d}",
            text=f"Turn {index}",
        )
        for index in range(1, count + 1)
    ]


def test_length_service_reports_balanced_strategy() -> None:
    service = TranscriptLengthService(evidence_index=EvidenceIndexService())
    assessment = service.assess_quotes(_make_quotes(200))
    assert assessment.quote_count == 200
    assert assessment.strategy == STRATEGY_BALANCED_SAMPLE
    assert assessment.warning is not None
    assert "strategy=balanced_sample" in assessment.warning


def test_length_assessment_api(monkeypatch) -> None:
    from config import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "evidence_prompt_max_quotes", 5)
    transcripts = TranscriptService()
    lines = "\n".join(f"Person A: line {index}" for index in range(1, 12))
    bundle = transcripts.ingest(lines, source_type=SourceType.PASTE, title="Long lines")
    transcripts.mark_ready(bundle.transcript.id)

    client = TestClient(app)
    response = client.get(f"/api/transcripts/{bundle.transcript.id}/length-assessment")
    assert response.status_code == 200
    body = response.json()
    assert body["quote_count"] >= 10
    assert body["max_quotes"] == 5
    assert body["strategy"] == STRATEGY_BALANCED_SAMPLE
    assert body["warning"] is not None
