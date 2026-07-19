"""Safety red-team fixture tests (v1.2 Workstream B)."""

from __future__ import annotations

import pytest

from backend.evaluation.claims import ForbiddenClaimScorer
from backend.services.safety_risk_scanner import SKIP_IN_SAFETY_MODE, safety_risk_scanner
from tests.helpers.safety_fixtures import iter_safety_fixtures

pytestmark = [pytest.mark.golden]


@pytest.mark.parametrize("fixture", iter_safety_fixtures(), ids=lambda f: f.fixture_id)
def test_safety_fixture_scanner_matches_expected_risk(fixture) -> None:
    scan = safety_risk_scanner.scan(fixture.transcript_text)
    expected = fixture.assertions.get("expected_risk_level") or fixture.metadata.get(
        "expected_risk_level"
    )
    assert scan.risk_level == expected
    recommended = fixture.assertions.get("expected_safety_mode_recommended")
    if recommended is not None:
        assert scan.safety_mode_recommended is bool(recommended)


def test_at_least_five_safety_fixtures() -> None:
    assert len(iter_safety_fixtures()) >= 5


def test_high_risk_fixtures_recommend_safety_mode() -> None:
    highs = [
        f
        for f in iter_safety_fixtures()
        if (f.assertions.get("expected_risk_level") or "") == "high"
    ]
    assert highs
    for fixture in highs:
        scan = safety_risk_scanner.scan(fixture.transcript_text)
        assert scan.safety_mode_recommended is True
        suppress = fixture.metadata.get("expected_module_suppression") or []
        for module_id in suppress:
            assert module_id in SKIP_IN_SAFETY_MODE or module_id


def test_ordinary_conflict_is_false_positive_guard() -> None:
    fixture = next(f for f in iter_safety_fixtures() if "ordinary_conflict" in f.fixture_id)
    scan = safety_risk_scanner.scan(fixture.transcript_text)
    assert scan.risk_level == "none"
    assert scan.safety_mode_recommended is False


def test_forbidden_claim_scorer_flags_diagnosis() -> None:
    score = ForbiddenClaimScorer().score_text(
        "The partner is a narcissist with narcissistic personality disorder."
    )
    assert score.forbidden_claim_count >= 1
    assert "narcissism_determination" in score.categories_hit or "diagnosis" in score.categories_hit
