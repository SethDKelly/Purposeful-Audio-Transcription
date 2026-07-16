"""Evidence index and quote traceability for golden transcripts."""

from __future__ import annotations

import pytest

from backend.domain.enums import SourceType
from backend.services.evidence_index import EvidenceIndexService
from backend.services.transcript_service import transcript_service
from tests.helpers.golden_transcripts import assert_required_quote_substrings

pytestmark = pytest.mark.golden


def test_required_quote_substrings_exist_in_transcripts(golden_fixture) -> None:
    assert_required_quote_substrings(golden_fixture)


def test_ingest_assigns_sequential_quote_ids(golden_fixture) -> None:
    bundle = transcript_service.ingest(
        raw_text=golden_fixture.labeled_text(),
        source_type=SourceType.PASTE,
        title=golden_fixture.metadata.get("title") or golden_fixture.fixture_id,
    )
    quotes = bundle.evidence_quotes
    assert len(quotes) >= 10
    for index, quote in enumerate(quotes, start=1):
        assert quote.quote_id == f"Q{index:03d}"
        assert quote.quote_index == index

    quote_ids = [quote.quote_id for quote in quotes]
    assert len(quote_ids) == len(set(quote_ids))
    assert all(qid.startswith("Q") for qid in quote_ids)

    speakers = {speaker.display_name or speaker.label for speaker in bundle.speakers}
    for name in golden_fixture.metadata.get("participants") or []:
        assert name in speakers


def test_evidence_index_generates_unique_quote_ids(golden_fixture) -> None:
    bundle = transcript_service.ingest(
        raw_text=golden_fixture.labeled_text(),
        source_type=SourceType.PASTE,
        title=golden_fixture.fixture_id,
    )
    service = EvidenceIndexService()
    rebuilt = service.build_index_from_turns(
        bundle.transcript.id,
        bundle.turns,
    )
    quote_ids = [quote.quote_id for quote in rebuilt]
    assert len(quote_ids) == len(set(quote_ids))
    assert quote_ids == [f"Q{index:03d}" for index in range(1, len(rebuilt) + 1)]

    for substring in golden_fixture.assertions.get("required_quote_substrings") or []:
        cited = "\n".join(quote.text for quote in rebuilt)
        assert substring in cited
