"""Load and evaluate golden transcript fixtures under tests/fixtures/golden_transcripts/."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

GOLDEN_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "golden_transcripts"

REQUIRED_FILES = frozenset(
    {
        "transcript.md",
        "transcript.json",
        "expected_signals.md",
        "metadata.yaml",
        "expected_assertions.yaml",
    }
)

HIGH_CONFIDENCE = frozenset({"high", "observed", "confirmed"})


@dataclass(frozen=True)
class GoldenFixture:
    path: Path
    metadata: dict[str, Any]
    transcript: dict[str, Any]
    assertions: dict[str, Any]
    transcript_markdown: str
    expected_signals_markdown: str

    @property
    def fixture_id(self) -> str:
        return str(
            self.metadata.get("fixture_id")
            or self.transcript.get("fixture_id")
            or self.assertions.get("fixture_id")
            or ""
        )

    def full_transcript_text(self) -> str:
        return "\n".join(
            (turn.get("text") or "").strip()
            for turn in self.transcript.get("turns") or []
            if (turn.get("text") or "").strip()
        )

    def labeled_text(self) -> str:
        """Convert JSON turns into parser-ready ``Speaker: text`` lines."""
        lines: list[str] = []
        for turn in self.transcript.get("turns") or []:
            speaker = (turn.get("speaker") or "Speaker").strip()
            text = (turn.get("text") or "").strip()
            if text:
                lines.append(f"{speaker}: {text}")
        return "\n".join(lines)


def list_golden_dirs() -> list[Path]:
    if not GOLDEN_ROOT.is_dir():
        return []
    return sorted(
        path
        for path in GOLDEN_ROOT.iterdir()
        if path.is_dir() and (path / "transcript.json").is_file()
    )


def load_golden_fixture(path: Path) -> GoldenFixture:
    transcript = json.loads((path / "transcript.json").read_text(encoding="utf-8"))
    metadata_path = path / "metadata.yaml"
    assertions_path = path / "expected_assertions.yaml"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Missing metadata.yaml in {path}")
    if not assertions_path.is_file():
        raise FileNotFoundError(f"Missing expected_assertions.yaml in {path}")
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
    assertions = yaml.safe_load(assertions_path.read_text(encoding="utf-8")) or {}
    return GoldenFixture(
        path=path,
        metadata=metadata,
        transcript=transcript,
        assertions=assertions,
        transcript_markdown=(path / "transcript.md").read_text(encoding="utf-8"),
        expected_signals_markdown=(path / "expected_signals.md").read_text(encoding="utf-8"),
    )


def load_golden_fixture_by_id(fixture_id: str) -> GoldenFixture:
    for path in list_golden_dirs():
        fixture = load_golden_fixture(path)
        if fixture.fixture_id == fixture_id:
            return fixture
    raise LookupError(f"No golden fixture with fixture_id={fixture_id!r}")


def iter_golden_fixtures() -> list[GoldenFixture]:
    return [load_golden_fixture(path) for path in list_golden_dirs()]


def text_contains_any(text: str, substrings: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(fragment.lower() in lowered for fragment in substrings)


def assert_required_quote_substrings(fixture: GoldenFixture) -> None:
    full_text = fixture.full_transcript_text()
    for substring in fixture.assertions.get("required_quote_substrings") or []:
        if substring not in full_text:
            raise AssertionError(
                f"{fixture.path.name}: required substring not found: {substring!r}"
            )


def assert_required_signals_reference_transcript(fixture: GoldenFixture) -> None:
    full_text = fixture.full_transcript_text()
    for signal in fixture.assertions.get("required_signals") or []:
        refs = signal.get("must_reference_any") or []
        if not text_contains_any(full_text, refs):
            raise AssertionError(
                f"{fixture.path.name} signal {signal.get('id')}: "
                f"none of {refs!r} found in transcript"
            )


def collect_findings(module_output: dict[str, Any]) -> list[dict[str, Any]]:
    findings = module_output.get("findings") or []
    return [finding for finding in findings if isinstance(finding, dict)]


def collect_constructs(module_output: dict[str, Any]) -> list[dict[str, Any]]:
    constructs = module_output.get("constructs") or []
    return [construct for construct in constructs if isinstance(construct, dict)]


def flatten_module_text(module_output: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("executive_summary", "raw_markdown_report"):
        value = module_output.get(key)
        if isinstance(value, str):
            parts.append(value)
    for finding in collect_findings(module_output):
        for key in ("title", "summary", "type"):
            value = finding.get(key)
            if isinstance(value, str):
                parts.append(value)
    for construct in collect_constructs(module_output):
        for key in ("label", "type"):
            value = construct.get(key)
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts)


def contains_signal(module_output: dict[str, Any], signal_type: str) -> bool:
    needle = signal_type.lower().replace("_", " ")
    compact_needle = signal_type.lower().replace("_", "")
    for finding in collect_findings(module_output):
        finding_type = str(finding.get("type") or "").lower()
        if needle in finding_type or compact_needle in finding_type.replace("_", ""):
            return True
        blob = " ".join(
            str(finding.get(key) or "")
            for key in ("title", "summary")
        ).lower()
        if needle in blob:
            return True
    for construct in collect_constructs(module_output):
        construct_type = str(construct.get("type") or "").lower()
        if needle in construct_type or compact_needle in construct_type.replace("_", ""):
            return True
    return needle in flatten_module_text(module_output).lower()


def cites_any(
    module_output: dict[str, Any],
    substrings: Iterable[str],
    *,
    quotes_by_id: dict[str, str] | None = None,
) -> bool:
    quote_ids: set[str] = set()
    for finding in collect_findings(module_output):
        for quote_id in finding.get("evidence_quote_ids") or []:
            quote_ids.add(str(quote_id))
    for construct in collect_constructs(module_output):
        for quote_id in construct.get("evidence_quote_ids") or []:
            quote_ids.add(str(quote_id))

    if quotes_by_id:
        cited_text = " ".join(quotes_by_id.get(qid, "") for qid in quote_ids)
        if text_contains_any(cited_text, substrings):
            return True

    return text_contains_any(flatten_module_text(module_output), substrings)


def validate_evidence_quote_ids(
    module_output: dict[str, Any],
    valid_quote_ids: Iterable[str],
) -> None:
    valid = set(valid_quote_ids)
    for finding in collect_findings(module_output):
        for quote_id in finding.get("evidence_quote_ids") or []:
            if quote_id not in valid:
                raise AssertionError(
                    f"Finding {finding.get('id')} cites unknown quote id {quote_id!r}"
                )
    for construct in collect_constructs(module_output):
        for quote_id in construct.get("evidence_quote_ids") or []:
            if quote_id not in valid:
                raise AssertionError(
                    f"Construct cites unknown quote id {quote_id!r}"
                )


def contains_high_confidence_claim(
    module_output: dict[str, Any],
    forbidden_term: str,
) -> bool:
    pattern = re.compile(re.escape(forbidden_term), re.IGNORECASE)
    for finding in collect_findings(module_output):
        confidence = str(finding.get("confidence") or "").lower()
        blob = " ".join(
            str(finding.get(key) or "")
            for key in ("title", "summary", "type")
        )
        if pattern.search(blob) and confidence in HIGH_CONFIDENCE:
            return True
    return bool(pattern.search(flatten_module_text(module_output)))


def forbidden_terms_in_output(
    module_output: dict[str, Any],
    forbidden_terms: Iterable[str],
) -> list[str]:
    text = flatten_module_text(module_output).lower()
    hits: list[str] = []
    for term in forbidden_terms:
        normalized = term.lower().replace("_", " ")
        if normalized in text or term.lower() in text:
            hits.append(term)
    return hits
