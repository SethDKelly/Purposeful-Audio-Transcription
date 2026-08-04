"""Phase 004 — evidence precision config, validation, index, and eval metrics."""

from __future__ import annotations

import json
from pathlib import Path

from backend.core.module_registry import ModuleRegistry
from backend.domain.enums import SourceType
from backend.domain.transcript import Speaker, Transcript, TranscriptBundle, Turn
from backend.evaluation.harness import EvalGateConfig, evaluate_module_output
from backend.services.evidence_index import EvidenceIndexService
from backend.services.evidence_precision import (
    display_text_for_quote,
    extract_primary_span,
    looks_like_paragraph,
)
from backend.services.module_output_validator import ModuleOutputValidator
from backend.services.output_parser import OutputParser
from backend.services.transcript_parser import ParsedTurn
from config.settings import settings
from tests.helpers.golden_transcripts import load_golden_fixture_by_id

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def _sample_output(module_id: str = "relationship_conversation_analysis"):
    registry = ModuleRegistry()
    module = registry.get(module_id)
    data = json.loads((FIXTURES / "sample_module_output.json").read_text(encoding="utf-8"))
    data["module_id"] = module.config.id
    data["module_version"] = module.config.version
    return (
        module,
        OutputParser().normalize(data, module, "run-precision"),
        {f"Q{index:03d}" for index in range(1, 5)},
    )


def test_evidence_precision_settings_defaults() -> None:
    assert settings.evidence_atomic_quote_max_chars == 280
    assert settings.evidence_short_exchange_max_turns == 4
    assert settings.evidence_context_window_before_turns == 1
    assert settings.evidence_context_window_after_turns == 1
    assert settings.evidence_max_items_per_finding == 3
    assert settings.evidence_prefer_sentence_spans is True
    assert settings.evidence_allow_paragraph_evidence is False
    assert settings.evidence_warning_threshold_chars == 360
    assert settings.evidence_hard_max_chars == 600


def test_framework_prompts_require_concise_evidence() -> None:
    shared = (ROOT / "config" / "framework" / "shared_instructions.md").read_text(
        encoding="utf-8"
    )
    schema = (ROOT / "config" / "framework" / "output_schema_instructions.md").read_text(
        encoding="utf-8"
    )
    assert "smallest useful" in shared.lower()
    assert "paragraph" in shared.lower()
    assert "smallest useful" in schema.lower()


def test_extract_primary_span_for_long_multi_sentence() -> None:
    long = (
        "I should have texted earlier. "
        "Then everything escalated and we both said things we regret. "
        "Still, I want to repair this tonight."
    )
    # Force above atomic max.
    padded = long + (" extra words." * 20)
    span = extract_primary_span(padded)
    assert span is not None
    assert span.startswith("I should have texted earlier")
    assert len(span) < len(padded)


def test_display_text_prefers_span() -> None:
    assert display_text_for_quote("full turn text", span_text="short") == "short"


def test_evidence_index_sets_type_and_context() -> None:
    import uuid
    from datetime import UTC, datetime

    transcript_id = str(uuid.uuid4())
    speaker_id = str(uuid.uuid4())
    turns = [
        Turn(
            id=str(uuid.uuid4()),
            transcript_id=transcript_id,
            speaker_id=speaker_id,
            turn_index=i,
            text=text,
        )
        for i, text in enumerate(
            ["Earlier turn.", "I should have texted.", "Later turn."], start=1
        )
    ]
    bundle = TranscriptBundle(
        transcript=Transcript(
            id=transcript_id,
            title="Precision",
            raw_text="x",
            source_type=SourceType.PASTE,
            created_at=datetime.now(UTC),
        ),
        speakers=[
            Speaker(
                id=speaker_id,
                transcript_id=transcript_id,
                label="Maya",
                display_name="Maya",
            )
        ],
        turns=turns,
    )
    parsed = [
        ParsedTurn(speaker_label="Maya", text=t.text) for t in turns
    ]
    quotes = EvidenceIndexService().build_index(
        bundle, parsed, {"Maya": speaker_id}
    )
    assert len(quotes) == 3
    mid = quotes[1]
    assert mid.quote_id == "Q002"
    assert mid.evidence_type == "atomic_quote"
    assert mid.context_before == "Earlier turn."
    assert mid.context_after == "Later turn."


def test_validator_warns_on_long_evidence() -> None:
    module, output, quote_ids = _sample_output()
    long_text = "x" * (settings.evidence_warning_threshold_chars + 10)
    texts = {qid: "short" for qid in quote_ids}
    texts["Q001"] = long_text
    result = ModuleOutputValidator().validate(
        output, module, quote_ids, quote_texts=texts
    )
    assert result.is_valid
    assert any("warning threshold" in w for w in result.warnings)


def test_validator_errors_on_hard_max_evidence() -> None:
    module, output, quote_ids = _sample_output()
    texts = {qid: "short" for qid in quote_ids}
    texts["Q001"] = "y" * (settings.evidence_hard_max_chars + 5)
    result = ModuleOutputValidator().validate(
        output, module, quote_ids, quote_texts=texts
    )
    assert not result.is_valid
    assert any("hard max" in e for e in result.errors)


def test_validator_errors_on_too_many_evidence_items() -> None:
    module, output, quote_ids = _sample_output()
    output.findings[0].evidence_quote_ids = ["Q001", "Q002", "Q003", "Q004"]
    texts = {qid: "ok" for qid in quote_ids}
    result = ModuleOutputValidator().validate(
        output, module, quote_ids, quote_texts=texts
    )
    assert not result.is_valid
    assert any("max 3" in e or "evidence items" in e for e in result.errors)


def test_validator_warns_on_paragraph_shaped_evidence() -> None:
    module, output, quote_ids = _sample_output()
    padded = (
        "First sentence here is long enough. "
        "Second sentence continues the idea further. "
        "Third sentence keeps going past the atomic limit intentionally."
        + (" More filler." * 20)
    )
    assert looks_like_paragraph(padded)
    texts = {qid: "short" for qid in quote_ids}
    texts["Q001"] = padded
    result = ModuleOutputValidator().validate(
        output, module, quote_ids, quote_texts=texts
    )
    assert any("paragraph" in w.lower() for w in result.warnings)


def test_eval_harness_reports_evidence_precision_metrics() -> None:
    fixture = load_golden_fixture_by_id("GT001")
    module, output, _quote_ids = _sample_output()
    payload = json.loads(output.model_dump_json())
    quote_texts = {
        "Q001": "I should have texted.",
        "Q002": "That is not fair.",
        "Q003": "ok",
        "Q004": "ok",
    }
    result = evaluate_module_output(
        fixture=fixture,
        module_id=module.config.id,
        module_output=payload,
        valid_quote_ids=set(quote_texts),
        quote_texts=quote_texts,
        gates=EvalGateConfig(
            min_required_signal_hit_rate=0.0,
            min_evidence_coverage_rate=0.0,
            max_average_evidence_chars=200,
            max_paragraph_evidence_count=0,
        ),
    )
    assert result.average_evidence_chars > 0
    assert result.paragraph_evidence_count == 0
    assert result.gate_passed


def test_eval_gate_fails_on_paragraph_evidence() -> None:
    fixture = load_golden_fixture_by_id("GT001")
    module, output, _quote_ids = _sample_output()
    payload = json.loads(output.model_dump_json())
    long_para = ("Sentence one. " * 40).strip()
    quote_texts = {"Q001": long_para, "Q002": "x", "Q003": "x", "Q004": "x"}
    result = evaluate_module_output(
        fixture=fixture,
        module_id=module.config.id,
        module_output=payload,
        valid_quote_ids=set(quote_texts),
        quote_texts=quote_texts,
        gates=EvalGateConfig(
            min_required_signal_hit_rate=0.0,
            min_evidence_coverage_rate=0.0,
            max_paragraph_evidence_count=0,
        ),
    )
    assert result.paragraph_evidence_count >= 1
    assert not result.gate_passed


def test_phase_004_doc_and_design_exist() -> None:
    phase = ROOT / "docs" / "planning" / "phases" / "004_v2_1_evidence_precision.md"
    design = ROOT / "docs" / "developer" / "evidence_precision_design.md"
    adr = (
        ROOT
        / "docs"
        / "developer"
        / "architecture_decisions"
        / "adr_002_concise_evidence_spans.md"
    )
    assert phase.is_file()
    assert design.is_file()
    assert adr.is_file()
    text = phase.read_text(encoding="utf-8")
    assert "Evidence Precision" in text
