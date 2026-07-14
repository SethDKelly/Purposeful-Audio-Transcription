#!/usr/bin/env python3
"""Print selected GitHub OIDC JWT claims (used by deploy-dev.yml debug step)."""

from __future__ import annotations

import base64
import json
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: decode-oidc-claims.py <base64url-payload>", file=sys.stderr)
        return 2
    payload = sys.argv[1].strip()
    padded = payload + "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(padded))
    print("GitHub OIDC token claims (compare sub to aws-backbone github_repositories):")
    for key in ("sub", "aud", "repository", "repository_owner", "ref"):
        if key in claims:
            print(f"  {key}: {claims[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
