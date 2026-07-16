"""Load and normalize golden transcript fixtures under tests/fixtures/golden_transcripts/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

GOLDEN_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "golden_transcripts"


@dataclass(frozen=True)
class GoldenFixture:
    path: Path
    metadata: dict[str, Any]
    transcript: dict[str, Any]
    assertions: dict[str, Any]

    @property
    def fixture_id(self) -> str:
        return str(self.metadata.get("fixture_id") or self.transcript.get("fixture_id") or "")

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
    )


def iter_golden_fixtures() -> list[GoldenFixture]:
    return [load_golden_fixture(path) for path in list_golden_dirs()]
