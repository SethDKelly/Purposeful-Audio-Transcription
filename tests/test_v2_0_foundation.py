"""v2.0 foundation: report package + safety event recording."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO

from backend.db.base import get_session
from backend.repositories.safety_event_repository import safety_event_repository
from backend.services.report_package_service import build_v1_report_package_zip
from backend.services.safety_risk_scanner import safety_risk_scanner


def test_build_v1_report_package_zip_manifest() -> None:
    package = build_v1_report_package_zip(
        workflow_run={
            "id": "run-1",
            "workflow_id": "quick_review",
            "transcript_id": "tx-1",
            "safety_mode": True,
        },
        synthesis={
            "id": "rep-1",
            "executive_summary": "Summary",
            "high_confidence_findings": [
                {
                    "id": "F1",
                    "title": "Theme",
                    "evidence_quote_ids": ["Q001"],
                    "confidence": "high",
                }
            ],
            "moderate_confidence_findings": [],
            "exploratory_hypotheses": [],
        },
        evidence_quotes=[{"quote_id": "Q001", "text": "Hello", "speaker_label": "A"}],
        module_lifecycle=[{"id": "nvc_analysis", "version": "1.0.0", "prompt_sha256": "abc"}],
    )
    with zipfile.ZipFile(BytesIO(package)) as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert "version_manifest.json" in names
        assert "findings_index.json" in names
        assert "evidence_appendix.md" in names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["finding_count"] == 1
        assert manifest["safety_mode"] is True
        assert "confidence_legend" in manifest


def test_safety_event_repository_roundtrip() -> None:
    scan = safety_risk_scanner.scan("I will kill you if you leave")
    assert scan.risk_level == "high"
    with get_session() as session:
        created = safety_event_repository.create(
            session,
            event_type="scan",
            risk_level=scan.risk_level,
            transcript_id="tx-risk-v2",
            categories=scan.matched_categories,
        )
        events = safety_event_repository.list_for_transcript(session, "tx-risk-v2")
    assert created["event_type"] == "scan"
    assert any(e["id"] == created["id"] for e in events)
