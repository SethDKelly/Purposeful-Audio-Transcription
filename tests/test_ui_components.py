from ui.api_client import module_display_name, module_name_map
from ui.components.evidence_quote_viewer import build_quotes_index, index_modules_by_quote


def test_module_name_map_uses_configured_names() -> None:
    modules = [
        {"id": "cognitive_analysis", "name": "Cognitive Analysis"},
        {"id": "meta_synthesis", "name": "Meta-Synthesis"},
    ]
    names = module_name_map(modules)
    assert module_display_name("cognitive_analysis", names) == "Cognitive Analysis"
    assert module_display_name("meta_synthesis", names) == "Meta-Synthesis"


def test_module_display_name_falls_back_to_title_case() -> None:
    assert module_display_name("bias_epistemic_quality", {}) == "Bias Epistemic Quality"


def test_build_quotes_index_enriches_speaker_names() -> None:
    quotes = [
        {
            "quote_id": "Q001",
            "speaker_id": "s1",
            "text": "Hello",
            "quote_index": 1,
        }
    ]
    speakers = [{"id": "s1", "label": "Person A", "display_name": "Alex"}]
    indexed = build_quotes_index(quotes, speakers)
    assert indexed["Q001"]["speaker_display_name"] == "Alex"


def test_index_modules_by_quote() -> None:
    module_runs = [
        {
            "module_id": "nvc_analysis",
            "parsed_output": {
                "module_id": "nvc_analysis",
                "findings": [{"evidence_quote_ids": ["Q001", "Q002"]}],
            },
        }
    ]
    usage = index_modules_by_quote(module_runs)
    assert usage["Q001"] == ["nvc_analysis"]
    assert usage["Q002"] == ["nvc_analysis"]
