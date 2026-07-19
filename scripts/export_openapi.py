#!/usr/bin/env python3
"""Dump OpenAPI JSON for typed-client generation.

Usage:
  python scripts/export_openapi.py > openapi.json
  npx openapi-typescript openapi.json -o frontend-react/src/api/generated.ts

The hand-maintained client in frontend-react/src/api/client.ts remains the
runtime client until generation is wired into CI.
"""

from __future__ import annotations

import json
import sys

from backend.main import app


def main() -> None:
    spec = app.openapi()
    json.dump(spec, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
