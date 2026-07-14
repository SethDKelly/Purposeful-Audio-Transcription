#!/usr/bin/env python3
"""Poll a workflow run until terminal status."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: poll_workflow_run.py <alb_base> <run_id>", file=sys.stderr)
        return 2
    base = sys.argv[1].rstrip("/")
    run_id = sys.argv[2]
    url = f"{base}/api/workflow-runs/{run_id}"
    out = sys.argv[3] if len(sys.argv) > 3 else None

    for attempt in range(1, 61):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.URLError as exc:
            print(f"[{attempt}] fetch error: {exc}", file=sys.stderr)
            time.sleep(15)
            continue

        data = json.loads(raw)
        status = data.get("status")
        modules = data.get("module_runs") or []
        parts = [f"{m.get('module_id')}={m.get('status')}" for m in modules]
        print(f"[{attempt}] status={status} modules={len(modules)} {' '.join(parts)}")
        if out:
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        if status in {"completed", "failed", "cancelled"}:
            for m in modules:
                print(
                    f"  {m.get('module_id')}: {m.get('status')} "
                    f"err={m.get('error_message')}"
                )
            print(f"final={status}")
            return 0 if status == "completed" else 1
        time.sleep(20)
    print("timed out waiting for workflow", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
