"""Golden fixture directory presence and file integrity."""

from __future__ import annotations

import pytest
import yaml

from tests.helpers.golden_transcripts import (
    GOLDEN_ROOT,
    REQUIRED_FILES,
    load_golden_fixture,
)

pytestmark = pytest.mark.golden


def test_golden_fixture_root_exists() -> None:
    assert GOLDEN_ROOT.is_dir()


def test_golden_fixture_directories_exist() -> None:
    fixture_dirs = [path for path in GOLDEN_ROOT.iterdir() if path.is_dir()]
    assert fixture_dirs, "No golden transcript fixture directories found"
    names = {path.name for path in fixture_dirs}
    assert "GT001_missed_dinner_couple" in names
    assert "GT002_caregiving_siblings" in names


def test_each_fixture_has_required_files() -> None:
    for fixture_dir in GOLDEN_ROOT.iterdir():
        if not fixture_dir.is_dir():
            continue
        present = {path.name for path in fixture_dir.iterdir()}
        missing = REQUIRED_FILES - present
        assert not missing, f"{fixture_dir.name} missing files: {sorted(missing)}"


def test_transcript_json_is_valid(golden_fixture) -> None:
    data = golden_fixture.transcript
    assert data.get("fixture_id")
    assert data.get("participants") or golden_fixture.metadata.get("participants")
    turns = data.get("turns") or []
    assert len(turns) >= 10
    for turn in turns:
        assert turn.get("speaker")
        assert (turn.get("text") or "").strip()


def test_yaml_files_are_valid(golden_fixture) -> None:
    meta = golden_fixture.metadata
    assertions = golden_fixture.assertions
    assert meta["fixture_id"]
    assert assertions["fixture_id"]
    assert meta["fixture_id"] == assertions["fixture_id"]
    assert isinstance(yaml.safe_load(yaml.safe_dump(meta)), dict)
    assert isinstance(yaml.safe_load(yaml.safe_dump(assertions)), dict)


def test_turn_ids_are_unique_if_present(golden_fixture) -> None:
    turn_ids = [
        turn.get("turn_id")
        for turn in golden_fixture.transcript.get("turns") or []
        if turn.get("turn_id")
    ]
    if turn_ids:
        assert len(turn_ids) == len(set(turn_ids))


def test_fixture_loader_round_trip() -> None:
    for path in sorted(GOLDEN_ROOT.iterdir()):
        if not path.is_dir():
            continue
        loaded = load_golden_fixture(path)
        assert loaded.fixture_id
        assert loaded.labeled_text().strip()
        assert loaded.expected_signals_markdown.strip()
