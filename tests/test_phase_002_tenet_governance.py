"""Phase 002 — core tenets and governance documentation integrity."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TENET_DOCS = (
    ROOT / "docs" / "product" / "core_tenets.md",
    ROOT / "docs" / "developer" / "pr_review_tenet_checklist.md",
    ROOT / "docs" / "evaluation" / "tenet_compliance_evaluation_plan.md",
)

INDEX_FILES_EXPECTING_TENET_REF = (
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "planning" / "README.md",
    ROOT / "docs" / "developer" / "architecture.md",
    ROOT / "docs" / "developer" / "contributing.md",
    ROOT / "docs" / "product" / "safety_aware_report_mode.md",
    ROOT / "docs" / "evaluation" / "golden_fixture_evaluation_plan.md",
)

EXPECTED_TENET_HEADINGS = (
    "Evidence Traceability",
    "Confidence Calibration",
    "Multi-Lens Analysis",
    "Non-Diagnostic Discipline",
    "Longitudinal Case Tracking",
    "Professional Workflow Fit",
    "Safety-Aware Framing",
    "Structured Reasoning Graph",
)

EVAL_DIMENSIONS = (
    "Evidence Traceability",
    "Confidence Calibration",
    "Multi-Lens Analysis",
    "Non-Diagnostic Discipline",
    "Longitudinal Case Tracking",
    "Professional Workflow Fit",
    "Safety-Aware Framing",
    "Structured Reasoning Graph",
)


@pytest.mark.parametrize("path", REQUIRED_TENET_DOCS, ids=lambda p: p.name)
def test_required_tenet_docs_exist(path: Path) -> None:
    assert path.is_file(), f"missing required tenet doc: {path.relative_to(ROOT)}"


def test_core_tenets_document_lists_all_eight_tenets() -> None:
    text = (ROOT / "docs" / "product" / "core_tenets.md").read_text(encoding="utf-8")
    for heading in EXPECTED_TENET_HEADINGS:
        assert heading in text, f"core_tenets.md missing tenet section: {heading}"
    assert "market-agnostic" in text.lower()


def test_pr_checklist_covers_tenet_sections() -> None:
    text = (
        ROOT / "docs" / "developer" / "pr_review_tenet_checklist.md"
    ).read_text(encoding="utf-8")
    for heading in EXPECTED_TENET_HEADINGS:
        assert heading in text, f"PR checklist missing section: {heading}"
    assert "Authentication / Privacy" in text


def test_tenet_compliance_eval_plan_has_dimensions() -> None:
    text = (
        ROOT / "docs" / "evaluation" / "tenet_compliance_evaluation_plan.md"
    ).read_text(encoding="utf-8")
    for dimension in EVAL_DIMENSIONS:
        assert dimension in text, f"eval plan missing dimension: {dimension}"
    assert "phases/002" in text.replace("\\", "/")
    assert "phases/009" in text.replace("\\", "/")


@pytest.mark.parametrize("path", INDEX_FILES_EXPECTING_TENET_REF, ids=lambda p: str(p.relative_to(ROOT)))
def test_indexes_reference_core_tenets(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "core_tenets" in text, f"{path.relative_to(ROOT)} should reference core_tenets"


def test_github_pr_template_exists_and_references_tenets() -> None:
    path = ROOT / ".github" / "pull_request_template.md"
    assert path.is_file(), "missing .github/pull_request_template.md"
    text = path.read_text(encoding="utf-8")
    assert "pr_review_tenet_checklist.md" in text
    assert "Evidence" in text
    assert "Non-diagnostic" in text
    assert "market-agnostic" in text.lower() or "Market-agnostic" in text


def test_active_phases_are_numeric_v2_1_sequence() -> None:
    phases_dir = ROOT / "docs" / "planning" / "phases"
    names = sorted(p.name for p in phases_dir.glob("*.md") if p.name != "README.md")
    expected = [
        "001_v2_1_phase_sequence_overview.md",
        "002_v2_1_core_tenets_and_governance.md",
        "003_v2_1_simple_email_auth_and_ownership.md",
        "004_v2_1_evidence_precision.md",
        "005_v2_1_evidence_snapshots_and_versioning.md",
        "006_v2_1_worker_atomicity_and_operational_safety.md",
        "007_v2_1_safety_policy_and_non_diagnostic_enforcement.md",
        "008_v2_1_graph_relationship_evidence_and_case_correctness.md",
        "009_v2_1_react_api_contract_and_release_candidate_readiness.md",
    ]
    assert names == expected
    assert not (phases_dir / "10_v2_1_cutover_auth_and_graph_depth.md").exists()


def test_phase_002_acceptance_markers() -> None:
    text = (
        ROOT / "docs" / "planning" / "phases" / "002_v2_1_core_tenets_and_governance.md"
    ).read_text(encoding="utf-8")
    # Remaining governance tasks should be checked off when phase completes.
    assert "- [x] Spot-check remaining backlog rows against tenets" in text
    assert "- [x] Add tenet checklist to PR template" in text
    assert "- [x] Add documentation stating that new features should preserve" in text
