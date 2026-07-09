from ui.components.evidence_quote_viewer import build_quotes_index, index_modules_by_quote


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
