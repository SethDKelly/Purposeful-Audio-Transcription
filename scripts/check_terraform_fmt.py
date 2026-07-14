"""Run terraform fmt -check when terraform is installed; skip otherwise."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "infra"


def main() -> int:
    if shutil.which("terraform") is None:
        print("terraform not on PATH; skipping fmt check")
        return 0
    if not INFRA.is_dir():
        print("infra/ missing; skipping")
        return 0
    result = subprocess.run(
        ["terraform", "fmt", "-check", "-recursive", str(INFRA)],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        print("terraform fmt -check failed; run: terraform fmt -recursive infra", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
