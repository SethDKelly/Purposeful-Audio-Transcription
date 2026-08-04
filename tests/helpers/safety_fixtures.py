"""Load safety red-team fixtures and assert scanner expectations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SAFETY_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "safety_red_team"


@dataclass(frozen=True)
class SafetyFixture:
    path: Path
    metadata: dict[str, Any]
    assertions: dict[str, Any]
    transcript_text: str

    @property
    def fixture_id(self) -> str:
        return str(self.metadata.get("fixture_id") or self.path.name)


def list_safety_dirs() -> list[Path]:
    if not SAFETY_ROOT.is_dir():
        return []
    return sorted(
        path
        for path in SAFETY_ROOT.iterdir()
        if path.is_dir() and (path / "transcript.txt").is_file()
    )


def load_safety_fixture(path: Path) -> SafetyFixture:
    return SafetyFixture(
        path=path,
        metadata=yaml.safe_load((path / "metadata.yaml").read_text(encoding="utf-8")) or {},
        assertions=yaml.safe_load((path / "expected_assertions.yaml").read_text(encoding="utf-8"))
        or {},
        transcript_text=(path / "transcript.txt").read_text(encoding="utf-8"),
    )


def iter_safety_fixtures() -> list[SafetyFixture]:
    return [load_safety_fixture(path) for path in list_safety_dirs()]
