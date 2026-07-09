from ui.components.report_exports import (
    build_workflow_report_json,
    build_workflow_report_markdown,
)


def test_build_workflow_report_markdown_includes_sections() -> None:
    workflow_run = {
        "id": "wf-1",
        "workflow_id": "quick_review",
        "status": "completed",
        "module_runs": [
            {
                "module_id": "nvc_analysis",
                "status": "completed",
                "parsed_output": {
                    "module_id": "nvc_analysis",
                    "executive_summary": "Needs and feelings appear.",
                    "raw_markdown_report": "## NVC\nDetail here.",
                    "findings": [],
                },
            }
        ],
    }
    synthesis = {
        "executive_summary": "Integrated view.",
        "convergence": ["Modules agree on repair."],
        "divergence": ["Different emphasis on needs."],
        "interventions": ["Validate before explaining."],
    }

    markdown = build_workflow_report_markdown(
        workflow_run,
        synthesis,
        workflow_name="Quick Review",
    )

    assert "# Quick Review Report" in markdown
    assert "## Convergence" in markdown
    assert "## Divergence" in markdown
    assert "### nvc_analysis" in markdown


def test_build_workflow_report_json_roundtrip() -> None:
    workflow_run = {"id": "wf-1", "status": "completed", "module_runs": []}
    synthesis = {"executive_summary": "Summary"}
    payload = build_workflow_report_json(workflow_run, synthesis, transcript_meta={"filename": "t.txt"})
    assert '"wf-1"' in payload
    assert "t.txt" in payload
