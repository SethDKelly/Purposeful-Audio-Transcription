from pathlib import Path

import pytest
import yaml

from backend.services.transcript_parser import TranscriptParser

TRANSCRIPTS_DIR = Path(__file__).parent / "fixtures" / "transcripts"
MANIFEST_PATH = TRANSCRIPTS_DIR / "manifest.yaml"


@pytest.fixture
def parser() -> TranscriptParser:
    return TranscriptParser()


def _load_manifest() -> list[dict]:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["transcripts"]


@pytest.mark.parametrize("scenario", _load_manifest(), ids=lambda item: item["id"])
def test_fixture_transcript_parses(parser: TranscriptParser, scenario: dict) -> None:
    text = (TRANSCRIPTS_DIR / scenario["file"]).read_text(encoding="utf-8")
    turns = parser.parse(text)

    assert len(turns) >= scenario["min_turns"]
    speaker_labels = {turn.speaker_label for turn in turns}
    assert len(speaker_labels) == scenario["expected_speakers"]


def test_golden_transcript_alias_matches_two_speaker_repair() -> None:
    golden = (Path(__file__).parent / "fixtures" / "golden_transcript.txt").read_text(
        encoding="utf-8"
    )
    repair = (TRANSCRIPTS_DIR / "two_speaker_repair.txt").read_text(encoding="utf-8")
    assert golden.strip() == repair.strip()
