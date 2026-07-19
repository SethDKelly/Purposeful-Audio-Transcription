"""Server-side report package builder (v2.0) — no ui/ dependency."""

from __future__ import annotations

import io
import json
import zipfile
from datetime import UTC, datetime
from typing import Any


def build_v1_report_package_zip(
    *,
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    evidence_quotes: list[dict[str, Any]] | None = None,
    structured: dict[str, Any] | None = None,
    module_lifecycle: list[dict[str, Any]] | None = None,
    redact: bool = False,
) -> bytes:
    """Professional package: manifest, report JSON, findings, evidence, versions."""
    evidence_quotes = evidence_quotes or []
    findings = []
    if synthesis:
        for bucket in (
            "high_confidence_findings",
            "moderate_confidence_findings",
            "exploratory_hypotheses",
        ):
            findings.extend(synthesis.get(bucket) or [])

    quote_ids: list[str] = []
    for f in findings:
        for qid in f.get("evidence_quote_ids") or []:
            if qid not in quote_ids:
                quote_ids.append(qid)

    quotes_by_id = {q.get("quote_id"): q for q in evidence_quotes if q.get("quote_id")}
    appendix_lines = [
        "# Evidence appendix",
        "",
        "Exploratory, non-diagnostic, evidence-limited analysis.",
        "",
    ]
    for qid in quote_ids:
        q = quotes_by_id.get(qid, {})
        text = q.get("text", "(quote text unavailable)")
        if redact:
            text = "[redacted]"
        speaker = q.get("speaker_label") or q.get("speaker") or "Speaker"
        appendix_lines.extend([f"## {qid}", f"- Speaker: {speaker}", f"- Text: {text}", ""])

    now = datetime.now(UTC).isoformat()
    manifest = {
        "schema_version": "1",
        "package_type": "rre_report_package",
        "created_at": now,
        "workflow_run_id": workflow_run.get("id"),
        "workflow_id": workflow_run.get("workflow_id"),
        "transcript_id": workflow_run.get("transcript_id"),
        "safety_mode": bool(workflow_run.get("safety_mode")),
        "finding_count": len(findings),
        "evidence_quote_count": len(quote_ids),
        "redacted": redact,
        "confidence_legend": {
            "high": "Strong evidence-linked claims",
            "moderate": "Plausible with partial evidence",
            "exploratory": "Hypotheses; treat cautiously",
        },
    }

    version_manifest = {
        "workflow_id": workflow_run.get("workflow_id"),
        "modules": module_lifecycle or [],
        "report_id": (synthesis or {}).get("id"),
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        zf.writestr("version_manifest.json", json.dumps(version_manifest, indent=2) + "\n")
        zf.writestr("report.json", json.dumps(synthesis or {}, indent=2) + "\n")
        zf.writestr("findings_index.json", json.dumps(findings, indent=2) + "\n")
        zf.writestr("evidence_appendix.md", "\n".join(appendix_lines).rstrip() + "\n")
        if structured:
            zf.writestr("structured_graph.json", json.dumps(structured, indent=2) + "\n")
        zf.writestr(
            "README.txt",
            "RRE report package (v2). See manifest.json for confidence legend and counts.\n",
        )
    return buf.getvalue()
