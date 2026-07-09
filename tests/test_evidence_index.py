import uuid
from datetime import UTC, datetime

import pytest

from backend.domain.enums import SourceType
from backend.domain.transcript import Speaker, Transcript, TranscriptBundle, Turn
from backend.services.evidence_index import EvidenceIndexService
from backend.services.transcript_parser import ParsedTurn


@pytest.fixture
def evidence_service() -> EvidenceIndexService:
    return EvidenceIndexService()


def test_build_index_assigns_stable_quote_ids(
    evidence_service: EvidenceIndexService,
) -> None:
    transcript_id = str(uuid.uuid4())
    speaker_id = str(uuid.uuid4())
    turn_id = str(uuid.uuid4())

    bundle = TranscriptBundle(
        transcript=Transcript(
            id=transcript_id,
            title="Test",
            raw_text="Person A: Hello",
            source_type=SourceType.PASTE,
            created_at=datetime.now(UTC),
        ),
        speakers=[
            Speaker(
                id=speaker_id,
                transcript_id=transcript_id,
                label="Person A",
                display_name="Person A",
            )
        ],
        turns=[
            Turn(
                id=turn_id,
                transcript_id=transcript_id,
                speaker_id=speaker_id,
                turn_index=1,
                text="Hello",
            )
        ],
    )
    parsed = [ParsedTurn(speaker_label="Person A", text="Hello")]

    quotes = evidence_service.build_index(bundle, parsed, {"Person A": speaker_id})
    assert len(quotes) == 1
    assert quotes[0].quote_id == "Q001"
    assert quotes[0].text == "Hello"


def test_lookup_by_quote_id(evidence_service: EvidenceIndexService) -> None:
    transcript_id = str(uuid.uuid4())
    speaker_id = str(uuid.uuid4())
    quotes = evidence_service.build_index(
        TranscriptBundle(
            transcript=Transcript(
                id=transcript_id,
                title="Test",
                raw_text="A: one\nB: two",
                source_type=SourceType.PASTE,
                created_at=datetime.now(UTC),
            ),
            speakers=[],
            turns=[
                Turn(
                    id=str(uuid.uuid4()),
                    transcript_id=transcript_id,
                    speaker_id=speaker_id,
                    turn_index=1,
                    text="one",
                ),
                Turn(
                    id=str(uuid.uuid4()),
                    transcript_id=transcript_id,
                    speaker_id=speaker_id,
                    turn_index=2,
                    text="two",
                ),
            ],
        ),
        [
            ParsedTurn(speaker_label="A", text="one"),
            ParsedTurn(speaker_label="B", text="two"),
        ],
        {"A": speaker_id, "B": speaker_id},
    )

    found = evidence_service.lookup_by_quote_id(quotes, "Q002")
    assert found is not None
    assert found.text == "two"
    assert quotes[1].context_before == "one"
