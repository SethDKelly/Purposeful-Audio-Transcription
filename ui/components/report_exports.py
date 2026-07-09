import json
from typing import Any


def build_workflow_report_markdown(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    workflow_name: str | None = None,
) -> str:
    lines = [
        f"# {workflow_name or workflow_run.get('workflow_id', 'Workflow')} Report",
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
    for module_run in workflow_run.get("module_runs", []):
        parsed = module_run.get("parsed_output") or {}
        module_id = parsed.get("module_id") or module_run.get("module_id", "module")
        lines.append(f"### {module_id}")
        lines.append(parsed.get("executive_summary", ""))
        lines.append("")
        report = parsed.get("raw_markdown_report", "").strip()
        if report:
            lines.append(report)
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def build_workflow_report_json(
    workflow_run: dict[str, Any],
    synthesis: dict[str, Any] | None,
    *,
    transcript_meta: dict[str, Any] | None = None,
) -> str:
    payload = {
        "workflow_run": workflow_run,
        "synthesis": synthesis,
        "transcript_meta": transcript_meta or {},
    }
    return json.dumps(payload, indent=2)
