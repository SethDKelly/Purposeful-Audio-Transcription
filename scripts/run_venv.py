"""Run a command with the project .venv interpreter when present."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def venv_python() -> Path:
    win = ROOT / ".venv" / "Scripts" / "python.exe"
    unix = ROOT / ".venv" / "bin" / "python"
    if win.is_file():
        return win
    if unix.is_file():
        return unix
    return Path(sys.executable)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: run_venv.py <script-or-module> [args...]", file=sys.stderr)
        return 2
    python = venv_python()
    env = os.environ.copy()
    # Prefer venv site-packages when re-invoked from system python.
    return subprocess.call([str(python), *sys.argv[1:]], cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
