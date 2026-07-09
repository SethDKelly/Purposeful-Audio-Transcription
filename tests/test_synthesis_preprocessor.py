import json
from pathlib import Path

from backend.domain.enums import ModuleRunStatus
from backend.repositories.module_run_repository import utc_now
from backend.services.synthesis_preprocessor import SynthesisPreprocessor

FIXTURES = Path(__file__).parent / "fixtures"


def _module_run(module_id: str, output: dict) -> ModuleRun:
    return ModuleRun(
        id=f"run-{module_id}",
        module_id=module_id,
        transcript_id="transcript-1",
        status=ModuleRunStatus.COMPLETED.value,
        parsed_output=output,
        created_at=utc_now(),
    )


def test_preprocessor_groups_findings_by_type() -> None:
    payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    runs = [
        _module_run("relationship_conversation_analysis", payload),
        _module_run(
            "nvc_analysis",
            {
                **payload,
                "module_id": "nvc_analysis",
                "findings": [
                    {
                        **payload["findings"][0],
                        "id": "F010",
                        "type": "need",
                        "title": "Need for consideration",
                    }
                ],
            },
        ),
    ]

    result = SynthesisPreprocessor().process(runs)

    assert "emotion" in result.findings_by_type
    assert "need" in result.findings_by_type
    assert {"Q001", "Q002", "Q004"}.issubset(result.allowed_quote_ids)


def test_preprocessor_detects_convergence_on_shared_quotes() -> None:
    payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    runs = [
        _module_run("relationship_conversation_analysis", payload),
        _module_run("systems_analysis", payload),
    ]

    result = SynthesisPreprocessor().process(runs)

    assert result.convergence
    assert "Q001" in result.convergence[0]


def test_preprocessor_detects_divergence_for_same_type_without_overlap() -> None:
    payload = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    nvc_payload = {
        **payload,
        "module_id": "nvc_analysis",
        "findings": [
            {
                "id": "F010",
                "type": "interaction_cycle",
                "title": "Unmet need cycle",
                "summary": "A need-expression pattern appears without shared quotes.",
                "confidence": "moderate",
                "evidence_quote_ids": ["Q003"],
                "alternative_explanations": ["stress"],
                "limitations": [],
            }
        ],
    }
    runs = [
        _module_run("relationship_conversation_analysis", payload),
        _module_run("nvc_analysis", nvc_payload),
    ]

    result = SynthesisPreprocessor().process(runs)

    assert result.divergence
    assert "nvc_analysis" in result.divergence[0]
