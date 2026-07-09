from ui.components.report_exports import (
    apply_export_redaction,
    build_coach_summary_markdown,
    build_mediation_brief_markdown,
    build_workflow_report_json,
    build_workflow_report_markdown,
    build_workflow_report_pdf,
)


def _sample_workflow_run() -> dict:
    return {
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
                    "findings": [
                        {
                            "title": "Unmet need for inclusion",
                            "summary": "Person A names feeling unheard.",
                            "confidence": "observed",
                            "evidence_quote_ids": ["Q001"],
                        }
                    ],
                    "recommendations": ["Validate before explaining intent."],
                    "limitations": ["Short excerpt only."],
                },
            }
        ],
    }


def _sample_synthesis() -> dict:
    return {
        "executive_summary": "Integrated view.",
        "convergence": ["Modules agree on repair."],
        "divergence": ["Different emphasis on needs."],
        "interventions": ["Validate before explaining."],
        "limitations": ["Synthesis uses module outputs only."],
    }


def test_build_workflow_report_markdown_includes_sections() -> None:
    markdown = build_workflow_report_markdown(
        _sample_workflow_run(),
        _sample_synthesis(),
        workflow_name="Quick Review",
    )

    assert "# Quick Review Report" in markdown
    assert "## Convergence" in markdown
    assert "## Divergence" in markdown
    assert "### nvc_analysis" in markdown
    assert "non-diagnostic" in markdown


def test_build_workflow_report_json_roundtrip() -> None:
    payload = build_workflow_report_json(
        _sample_workflow_run(),
        _sample_synthesis(),
        transcript_meta={"filename": "t.txt"},
    )
    assert '"wf-1"' in payload
    assert "t.txt" in payload


def test_build_workflow_report_pdf_returns_pdf_bytes() -> None:
    pdf_bytes = build_workflow_report_pdf(
        _sample_workflow_run(),
        _sample_synthesis(),
        workflow_name="Quick Review",
    )
    assert pdf_bytes.startswith(b"%PDF")


def test_build_coach_summary_markdown() -> None:
    markdown = build_coach_summary_markdown(
        _sample_workflow_run(),
        _sample_synthesis(),
        workflow_name="Quick Review",
    )
    assert "# Coach Summary" in markdown
    assert "## Priority themes" in markdown
    assert "Unmet need for inclusion" in markdown
    assert "## Suggested next steps" in markdown


def test_build_mediation_brief_markdown() -> None:
    workflow_run = _sample_workflow_run()
    workflow_run["module_runs"].append(
        {
            "module_id": "mediation_analysis",
            "status": "completed",
            "parsed_output": {
                "module_id": "mediation_analysis",
                "executive_summary": "Interests differ on timing.",
                "findings": [
                    {
                        "title": "Position vs interest",
                        "summary": "One party focuses on schedule certainty.",
                        "confidence": "moderate",
                        "evidence_quote_ids": ["Q002"],
                    }
                ],
            },
        }
    )
    markdown = build_mediation_brief_markdown(
        workflow_run,
        _sample_synthesis(),
        workflow_name="Mediation Brief",
    )
    assert "# Mediation Brief" in markdown
    assert "## Shared ground" in markdown
    assert "Interests differ on timing." in markdown


def test_apply_export_redaction_replaces_speaker_labels() -> None:
    text = "Person A told Person B they felt unheard."
    redacted = apply_export_redaction(text)
    assert "Person A" not in redacted
    assert "Participant" in redacted


def test_build_workflow_report_markdown_redact_skips_raw_module_report() -> None:
    markdown = build_workflow_report_markdown(
        _sample_workflow_run(),
        _sample_synthesis(),
        workflow_name="Quick Review",
        redact=True,
    )
    assert "## NVC" not in markdown
    assert "Participant" in markdown or "Person A" not in markdown
