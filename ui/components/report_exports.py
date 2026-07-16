import json
import re
from typing import Any

from fpdf import FPDF

_DISCLAIMER = (
    "Exploratory, non-diagnostic, evidence-limited analysis. "
    "Not a substitute for professional assessment."
)


def _module_runs(workflow_run: dict[str, Any]) -> list[dict[str, Any]]:
    return workflow_run.get("module_runs", [])


def _parsed_module_runs(workflow_run: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    items: list[tuple[str, dict[str, Any]]] = []
    for module_run in _module_runs(workflow_run):
        parsed = module_run.get("parsed_output") or {}
        module_id = parsed.get("module_id") or module_run.get("module_id", "module")
        items.append((module_id, parsed))
    return items


def _top_findings(
    workflow_run: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for _, parsed in _parsed_module_runs(workflow_run):
        findings.extend(parsed.get("findings", []))
    priority = {
        "observed": 0,
        "high": 1,
        "moderate": 2,
        "low": 3,
        "exploratory": 4,
        "insufficient_evidence": 5,
    }
    findings.sort(key=lambda item: priority.get(item.get("confidence", "low"), 9))
    return findings[:limit]


def _module_output(workflow_run: dict[str, Any], module_id: str) -> dict[str, Any] | None:
    for current_id, parsed in _parsed_module_runs(workflow_run):
        if current_id == module_id:
            return parsed
    return None


def apply_export_redaction(text: str) -> str:
    """Remove common speaker-label patterns for safer sharing."""
    redacted = re.sub(r"\bPerson [A-Z]\b", "Participant", text)
    redacted = re.sub(r"\bSpeaker \d+\b", "Participant", redacted)
    return redacted


def build_workflow_report_markdown(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
    redact: bool = False,
) -> str:
    lines = [
        f"# {workflow_name or workflow_run.get('workflow_id', 'Workflow')} Report",
        "",
        f"> {_DISCLAIMER}",
        "",
        f"**Workflow run:** {workflow_run.get('id')}",
        f"**Status:** {workflow_run.get('status')}",
        "",
    ]

    if synthesis:
        lines.extend(
            [
                "## Executive Summary",
                synthesis.get("executive_summary", ""),
                "",
            ]
        )
        if synthesis.get("convergence"):
            lines.append("## Convergence")
            lines.extend(f"- {item}" for item in synthesis["convergence"])
            lines.append("")
        if synthesis.get("divergence"):
            lines.append("## Divergence")
            lines.extend(f"- {item}" for item in synthesis["divergence"])
            lines.append("")
        if synthesis.get("interventions"):
            lines.append("## Interventions")
            lines.extend(f"- {item}" for item in synthesis["interventions"])
            lines.append("")

    lines.append("## Module Reports")
    for module_run in _module_runs(workflow_run):
        parsed = module_run.get("parsed_output") or {}
        module_id = parsed.get("module_id") or module_run.get("module_id", "module")
        lines.append(f"### {module_id}")
        lines.append(parsed.get("executive_summary", ""))
        lines.append("")
        if not redact:
            report = parsed.get("raw_markdown_report", "").strip()
            if report:
                lines.append(report)
                lines.append("")

    markdown = "\n".join(lines).strip() + "\n"
    return apply_export_redaction(markdown) if redact else markdown


def build_coach_summary_markdown(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
    redact: bool = False,
) -> str:
    snapshot = ""
    if synthesis and synthesis.get("executive_summary"):
        snapshot = synthesis["executive_summary"]
    else:
        summaries = [
            parsed.get("executive_summary", "")
            for _, parsed in _parsed_module_runs(workflow_run)
            if parsed.get("executive_summary")
        ]
        snapshot = summaries[0] if summaries else "No summary available."

    interventions: list[str] = []
    if synthesis and synthesis.get("interventions"):
        interventions = synthesis["interventions"]
    else:
        for _, parsed in _parsed_module_runs(workflow_run):
            interventions.extend(parsed.get("recommendations", []))

    limitations: list[str] = []
    if synthesis and synthesis.get("limitations"):
        limitations = synthesis["limitations"]
    for _, parsed in _parsed_module_runs(workflow_run):
        limitations.extend(parsed.get("limitations", []))

    lines = [
        f"# Coach Summary — {workflow_name or workflow_run.get('workflow_id', 'Workflow')}",
        "",
        f"> {_DISCLAIMER}",
        "",
        "## Snapshot",
        snapshot,
        "",
        "## Priority themes",
    ]
    for finding in _top_findings(workflow_run, limit=5):
        quote_ids = ", ".join(finding.get("evidence_quote_ids", []))
        evidence = f" ({quote_ids})" if quote_ids else ""
        lines.append(
            f"- **{finding.get('title', 'Finding')}** — {finding.get('summary', '')}{evidence}"
        )
    lines.append("")

    if interventions:
        lines.append("## Suggested next steps")
        for item in interventions[:5]:
            lines.append(f"- {item}")
        lines.append("")

    if limitations:
        lines.append("## Caveats")
        for item in limitations[:5]:
            lines.append(f"- {item}")
        lines.append("")

    markdown = "\n".join(lines).strip() + "\n"
    return apply_export_redaction(markdown) if redact else markdown


def build_mediation_brief_markdown(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
    redact: bool = False,
) -> str:
    mediation = _module_output(workflow_run, "mediation_analysis")
    mediation_summary = mediation.get("executive_summary", "") if mediation else ""

    lines = [
        f"# Mediation Brief — {workflow_name or workflow_run.get('workflow_id', 'Workflow')}",
        "",
        f"> {_DISCLAIMER}",
        "",
        "## Neutral overview",
        synthesis.get("executive_summary", mediation_summary) if synthesis else mediation_summary,
        "",
    ]

    if mediation_summary and synthesis and synthesis.get("executive_summary"):
        lines.extend(["## Mediation lens", mediation_summary, ""])

    if synthesis and synthesis.get("convergence"):
        lines.append("## Shared ground")
        lines.extend(f"- {item}" for item in synthesis["convergence"])
        lines.append("")

    if synthesis and synthesis.get("divergence"):
        lines.append("## Differences to explore")
        lines.extend(f"- {item}" for item in synthesis["divergence"])
        lines.append("")

    if mediation:
        lines.append("## Mediation findings")
        for finding in mediation.get("findings", [])[:6]:
            lines.append(f"- **{finding.get('title', 'Finding')}** — {finding.get('summary', '')}")
        lines.append("")

    next_steps = synthesis.get("interventions", []) if synthesis else []
    if not next_steps:
        for _, parsed in _parsed_module_runs(workflow_run):
            next_steps.extend(parsed.get("recommendations", []))
    if next_steps:
        lines.append("## Process next steps")
        for item in next_steps[:5]:
            lines.append(f"- {item}")
        lines.append("")

    markdown = "\n".join(lines).strip() + "\n"
    return apply_export_redaction(markdown) if redact else markdown


def build_workflow_report_json(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    transcript_meta: dict[str, Any] | None = None,
    redact: bool = False,
) -> str:
    payload = {
        "workflow_run": workflow_run,
        "synthesis": synthesis,
        "transcript_meta": transcript_meta or {},
        "disclaimer": _DISCLAIMER,
    }
    text = json.dumps(payload, indent=2)
    return apply_export_redaction(text) if redact else text


def _pdf_safe(text: str) -> str:
    replacements = {
        "—": "-",
        "•": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _plain_pdf_line(line: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return _pdf_safe(text)


def build_workflow_report_pdf(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
    redact: bool = False,
) -> bytes:
    markdown = build_workflow_report_markdown(
        workflow_run,
        synthesis,
        workflow_name=workflow_name,
        redact=redact,
    )
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    width = pdf.epw

    for line in markdown.splitlines():
        clean = _plain_pdf_line(line.rstrip())
        if not clean:
            pdf.ln(4)
            continue
        if clean.startswith("# "):
            pdf.set_font("Helvetica", style="B", size=14)
            pdf.multi_cell(width, 8, clean[2:])
            pdf.set_font("Helvetica", size=11)
            continue
        if clean.startswith("## "):
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.multi_cell(width, 7, clean[3:])
            pdf.set_font("Helvetica", size=11)
            continue
        if clean.startswith("### "):
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.multi_cell(width, 6, clean[4:])
            pdf.set_font("Helvetica", size=11)
            continue
        if clean.startswith("> "):
            pdf.set_font("Helvetica", style="I", size=10)
            pdf.multi_cell(width, 5, clean[2:])
            pdf.set_font("Helvetica", size=11)
            continue
        if clean.startswith("- "):
            pdf.multi_cell(width, 5, f"  - {clean[2:]}")
            continue
        pdf.multi_cell(width, 5, clean)

    return bytes(pdf.output())


def build_evidence_appendix_markdown(
    workflow_run: dict[str, Any],
    *,
    quotes_by_id: dict[str, dict[str, Any]] | None = None,
    redact: bool = False,
) -> str:
    quotes_by_id = quotes_by_id or {}
    lines = ["# Evidence appendix", "", _DISCLAIMER, ""]
    seen: set[str] = set()
    for _, parsed in _parsed_module_runs(workflow_run):
        for finding in parsed.get("findings", []):
            for quote_id in finding.get("evidence_quote_ids", []):
                if quote_id in seen:
                    continue
                seen.add(quote_id)
                quote = quotes_by_id.get(quote_id, {})
                text = quote.get("text", "(quote text unavailable)")
                speaker = quote.get("speaker") or quote.get("speaker_label") or "Speaker"
                lines.append(f"## {quote_id}")
                lines.append(f"- Speaker: {speaker}")
                lines.append(f"- Text: {text}")
                lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    return apply_export_redaction(content) if redact else content


def build_report_package_zip(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
    transcript_meta: dict[str, Any] | None = None,
    quotes_by_id: dict[str, dict[str, Any]] | None = None,
    redact: bool = False,
) -> bytes:
    """Manifest + report + evidence appendix package (v0.9 P5)."""
    import io
    import zipfile
    from datetime import UTC, datetime

    report_md = build_workflow_report_markdown(
        workflow_run,
        synthesis,
        workflow_name=workflow_name,
        redact=redact,
    )
    appendix = build_evidence_appendix_markdown(
        workflow_run,
        quotes_by_id=quotes_by_id,
        redact=redact,
    )
    report_json = build_workflow_report_json(
        workflow_run,
        synthesis,
        transcript_meta=transcript_meta,
        redact=redact,
    )
    findings: list[dict[str, Any]] = []
    for module_id, parsed in _parsed_module_runs(workflow_run):
        for finding in parsed.get("findings", []):
            findings.append(
                {
                    "module_id": module_id,
                    "id": finding.get("id"),
                    "title": finding.get("title"),
                    "confidence": finding.get("confidence"),
                    "evidence_quote_ids": finding.get("evidence_quote_ids", []),
                }
            )
    manifest = {
        "package_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "workflow_run_id": workflow_run.get("id"),
        "workflow_id": workflow_run.get("workflow_id"),
        "workflow_name": workflow_name,
        "transcript_id": (transcript_meta or {}).get("transcript_id"),
        "redacted": redact,
        "files": [
            "manifest.json",
            "report.md",
            "report.json",
            "evidence_appendix.md",
            "findings_index.json",
        ],
        "finding_count": len(findings),
        "disclaimer": _DISCLAIMER,
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        archive.writestr("report.md", report_md)
        archive.writestr("report.json", report_json)
        archive.writestr("evidence_appendix.md", appendix)
        archive.writestr("findings_index.json", json.dumps(findings, indent=2))
    return buffer.getvalue()
