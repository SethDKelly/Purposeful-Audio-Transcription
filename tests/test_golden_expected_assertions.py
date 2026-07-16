"""Schema and signal assertion structure for golden fixtures."""

from __future__ import annotations

import pytest

from tests.helpers.golden_transcripts import (
    assert_required_quote_substrings,
    assert_required_signals_reference_transcript,
    iter_golden_fixtures,
)

pytestmark = pytest.mark.golden


def test_expected_assertions_have_required_sections(golden_fixture) -> None:
    assertions = golden_fixture.assertions
    assert "fixture_id" in assertions
    assert "required_signals" in assertions
    assert "forbidden_or_low_confidence" in assertions
    assert "confidence_expectations" in assertions
    assert "required_quote_substrings" in assertions


def test_required_signals_are_well_formed(golden_fixture) -> None:
    for signal in golden_fixture.assertions.get("required_signals") or []:
        assert signal.get("id"), f"{golden_fixture.path.name} signal missing id"
        assert signal.get("type"), f"{golden_fixture.path.name} signal missing type"
        assert signal.get("description"), (
            f"{golden_fixture.path.name} signal {signal.get('id')} missing description"
        )
        assert signal.get("must_reference_any"), (
            f"{golden_fixture.path.name} signal {signal.get('id')} missing must_reference_any"
        )


def test_metadata_has_evaluation_fields(golden_fixture) -> None:
    meta = golden_fixture.metadata
    assert meta.get("title")
    assert meta.get("description")
    assert meta.get("relationship_type")
    assert meta.get("participants")
    assert meta.get("expected_constructs")
    assert meta.get("not_expected_or_low_confidence")
    assert meta.get("recommended_test_level")


def test_required_quote_substrings_exist_in_transcripts(golden_fixture) -> None:
    assert_required_quote_substrings(golden_fixture)


def test_required_signals_reference_transcript_text(golden_fixture) -> None:
    assert_required_signals_reference_transcript(golden_fixture)


def test_fixture_ids_are_unique_across_catalog() -> None:
    ids = [fixture.fixture_id for fixture in iter_golden_fixtures()]
    assert len(ids) == len(set(ids))
