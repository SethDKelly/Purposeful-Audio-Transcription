import uuid
from datetime import UTC, datetime

import pytest

from backend.domain.enums import SourceType
from backend.domain.transcript import EvidenceQuote, Speaker, Transcript, TranscriptBundle, Turn
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


def _make_quote(quote_index: int, speaker_id: str, transcript_id: str = "t1") -> EvidenceQuote:
    return EvidenceQuote(
        id=str(uuid.uuid4()),
        transcript_id=transcript_id,
        turn_id=str(uuid.uuid4()),
        speaker_id=speaker_id,
        quote_index=quote_index,
        quote_id=f"Q{quote_index:03d}",
        text=f"Turn {quote_index}",
    )


def test_select_quotes_for_prompt_returns_all_when_under_limit(
    evidence_service: EvidenceIndexService,
) -> None:
    speaker_id = str(uuid.uuid4())
    quotes = [_make_quote(index, speaker_id) for index in range(1, 6)]

    selected, note, strategy = evidence_service.select_quotes_for_prompt(quotes, max_quotes=10)
    assert len(selected) == 5
    assert note is None
    assert strategy == "full"


def test_select_quotes_for_prompt_summarizes_long_transcripts(
    evidence_service: EvidenceIndexService,
) -> None:
    speaker_id = str(uuid.uuid4())
    quotes = [_make_quote(index, speaker_id) for index in range(1, 151)]

    selected, note, strategy = evidence_service.select_quotes_for_prompt(
        quotes,
        max_quotes=120,
        head_quotes=80,
        tail_quotes=40,
        strategy="head_tail",
    )
    assert len(selected) == 120
    assert note is not None
    assert strategy == "head_tail"
    assert "strategy=head_tail" in note
    assert "30 of 150" in note
    assert selected[0].quote_id == "Q001"
    assert selected[-1].quote_id == "Q150"


def test_format_for_prompt_includes_omission_note(
    evidence_service: EvidenceIndexService,
) -> None:
    speaker_id = str(uuid.uuid4())
    transcript_id = str(uuid.uuid4())
    quotes = [_make_quote(index, speaker_id, transcript_id) for index in range(1, 151)]
    speakers = [
        Speaker(
            id=speaker_id,
            transcript_id=transcript_id,
            label="Person A",
            display_name="Person A",
        )
    ]

    formatted = evidence_service.format_for_prompt(
        quotes,
        speakers,
        max_quotes=120,
        head_quotes=80,
        tail_quotes=40,
    )

    assert "[Q001]" in formatted
    assert "[Q150]" in formatted
    assert "evidence quotes omitted" in formatted
    assert "[Q081]" not in formatted


def test_select_quotes_balanced_sample_includes_middle(
    evidence_service: EvidenceIndexService,
) -> None:
    speaker_id = str(uuid.uuid4())
    quotes = [_make_quote(index, speaker_id) for index in range(1, 151)]

    selected, note, strategy = evidence_service.select_quotes_for_prompt(
        quotes,
        max_quotes=120,
    )
    assert strategy == "balanced_sample"
    assert note is not None
    assert "strategy=balanced_sample" in note
    assert len(selected) == 120
    middle_ids = {quote.quote_id for quote in selected if 81 <= quote.quote_index <= 110}
    assert middle_ids, "balanced_sample should include middle-region quotes"
