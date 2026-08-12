#!/usr/bin/env python3
"""Verify Alembic revision modules import (cloud image / CI smoke)."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    versions = root / "alembic" / "versions"
    for path in sorted(versions.glob("*.py")):
        if path.name.startswith("__"):
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load migration module: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"OK {path.name}")

    from backend.db.migrations import upgrade_head  # noqa: F401

    print("migration imports OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
