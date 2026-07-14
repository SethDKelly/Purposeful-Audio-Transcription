"""Parse YAML/YML files used by the product and CI (syntax only)."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

GLOBS = (
    "config/**/*.yaml",
    "config/**/*.yml",
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "tests/fixtures/**/*.yaml",
)


def iter_yaml_files() -> list[Path]:
    files: list[Path] = []
    for pattern in GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted({path.resolve() for path in files if path.is_file()})


def main() -> int:
    errors: list[str] = []
    files = iter_yaml_files()
    if not files:
        print("No YAML files found to validate", file=sys.stderr)
        return 1

    for path in files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("YAML syntax validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"YAML OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
