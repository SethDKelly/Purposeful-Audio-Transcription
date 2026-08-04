#!/usr/bin/env python3
"""Fail if ui/ imports backend services, repositories, db, or providers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = ROOT / "ui"

FORBIDDEN = re.compile(
    r"^\s*(?:from|import)\s+backend\.(?:services|repositories|db|api|worker)\b"
)


def main() -> int:
    violations: list[str] = []
    for path in sorted(UI_ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if FORBIDDEN.search(line):
                rel = path.relative_to(ROOT).as_posix()
                violations.append(f"{rel}:{i}: {line.strip()}")
    if violations:
        print("UI/API boundary violations (ui must not import backend internals):")
        for item in violations:
            print(f"  {item}")
        return 1
    print("UI/API boundary OK (no forbidden backend imports in ui/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
