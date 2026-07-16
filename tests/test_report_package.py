"""Report package export tests (v0.9 P5)."""

import json
import zipfile
from io import BytesIO

from ui.components.report_exports import build_report_package_zip


def test_build_report_package_zip_contains_manifest_and_appendix() -> None:
    workflow_run = {
        "id": "wf-1",
        "workflow_id": "quick_review",
        "module_runs": [
            {
                "module_id": "nvc_analysis",
                "parsed_output": {
                    "module_id": "nvc_analysis",
                    "executive_summary": "Summary",
                    "findings": [
                        {
                            "id": "F001",
                            "title": "Theme",
                            "confidence": "moderate",
                            "evidence_quote_ids": ["Q001"],
                            "summary": "Summary text",
                        }
                    ],
                },
            }
        ],
    }
    package = build_report_package_zip(
        workflow_run,
        {"executive_summary": "Synth"},
        workflow_name="Quick Review",
        transcript_meta={"transcript_id": "tx-1"},
        quotes_by_id={"Q001": {"quote_id": "Q001", "text": "Hello", "speaker": "A"}},
        redact=False,
    )
    with zipfile.ZipFile(BytesIO(package)) as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert "report.md" in names
        assert "evidence_appendix.md" in names
        assert "findings_index.json" in names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["finding_count"] == 1
        appendix = archive.read("evidence_appendix.md").decode("utf-8")
        assert "Q001" in appendix
