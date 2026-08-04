#!/usr/bin/env python3
"""Fail if Python cache artifacts are tracked by git (v1.1 hygiene)."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "**/*.pyc", "**/__pycache__/**", "*.py[cod]"],
        check=False,
        capture_output=True,
    )
    # git ls-files with globs is pathspec; also list common names explicitly
    result2 = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    bad = [
        line
        for line in result2.stdout.splitlines()
        if line.endswith(".pyc")
        or line.endswith(".pyo")
        or "/__pycache__/" in line.replace("\\", "/")
        or line.replace("\\", "/").endswith("/__pycache__")
    ]
    if bad:
        print("Tracked Python cache artifacts (remove from git):", file=sys.stderr)
        for path in bad:
            print(f"  {path}", file=sys.stderr)
        return 1
    print("OK: no tracked __pycache__ / .pyc files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
