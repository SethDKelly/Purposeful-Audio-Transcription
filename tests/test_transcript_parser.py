import pytest

from backend.core.exceptions import TranscriptValidationError
from backend.services.transcript_parser import TranscriptParser


@pytest.fixture
def parser() -> TranscriptParser:
    return TranscriptParser()


def test_parse_two_speaker_transcript(parser: TranscriptParser) -> None:
    text = """Person A: I don't feel heard.
Person B: I was trying to explain my side.
Person A: That's not what I mean."""

    turns = parser.parse(text)
    assert len(turns) == 3
    assert turns[0].speaker_label == "Person A"
    assert "don't feel heard" in turns[0].text
    assert turns[1].speaker_label == "Person B"
    assert turns[2].speaker_label == "Person A"


def test_parse_multiline_continuation(parser: TranscriptParser) -> None:
    text = """Alice: I need more clarity.
Can you explain what happened?
Bob: Sure, I thought we agreed."""

    turns = parser.parse(text)
    assert len(turns) == 2
    assert turns[0].speaker_label == "Alice"
    assert "clarity" in turns[0].text
    assert "explain what happened" in turns[0].text
    assert turns[1].speaker_label == "Bob"


def test_parse_unlabeled_fallback(parser: TranscriptParser) -> None:
    text = "This is a single block without speaker labels."

    turns = parser.parse(text)
    assert len(turns) == 1
    assert turns[0].speaker_label == "Speaker 1"
    assert "single block" in turns[0].text


def test_parse_empty_raises(parser: TranscriptParser) -> None:
    with pytest.raises(TranscriptValidationError):
        parser.parse("   ")
