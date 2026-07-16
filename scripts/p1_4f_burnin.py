"""P1-4f AWS burn-in: ingest + research_oriented + full_multidisciplinary."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else (
    "http://rre-dev-alb-1066740987.us-east-2.elb.amazonaws.com"
)
# Optional: resume existing runs instead of starting new ones.
# python scripts/p1_4f_burnin.py <alb> [research_run_id] [full_multi_run_id] [transcript_id]
RESUME_RESEARCH = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
RESUME_FULL = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
RESUME_TRANSCRIPT = sys.argv[4] if len(sys.argv) > 4 else None

FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "golden_transcript.txt"
POLL_SECONDS = 20
MAX_WAIT = {
    "research_oriented": 60 * 60,
    "full_multidisciplinary": 120 * 60,
}


def http_json(method: str, path: str, body: dict | None = None, timeout: float = 180):
    import os

    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    api_key = os.environ.get("API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers=headers,
    )
    last_err: Exception | None = None
    for attempt in range(1, 9):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if raw else {}
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            code = getattr(exc, "code", None)
            # 504 while Bedrock holds the only API task is common — retry.
            if code not in {502, 503, 504, None} and not isinstance(exc, TimeoutError):
                if isinstance(exc, urllib.error.HTTPError):
                    detail = exc.read()[:300]
                    raise RuntimeError(f"HTTP {code} {path}: {detail!r}") from exc
                raise
            print(f"  retry {attempt}/8 after {type(exc).__name__} {code} on {method} {path}")
            time.sleep(min(5 * attempt, 30))
            # recreate request (HTTPError may consume body)
            req = urllib.request.Request(
                f"{BASE}{path}",
                data=data,
                method=method,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
    raise RuntimeError(f"gave up on {method} {path}: {last_err}")


def poll_run(workflow_id: str, run_id: str) -> dict:
    deadline = time.time() + MAX_WAIT[workflow_id]
    final: dict = {}
    while time.time() < deadline:
        time.sleep(POLL_SECONDS)
        try:
            _, final = http_json("GET", f"/api/workflow-runs/{run_id}")
        except Exception as exc:  # noqa: BLE001
            print(f"  poll error (will continue): {exc}")
            continue
        st = final.get("status")
        modules = final.get("module_runs") or []
        done = sum(1 for mr in modules if mr.get("status") in {"completed", "failed"})
        total = max(len(modules), 1)
        print(f"  poll status={st} modules={done}/{total}")
        if st in {"completed", "failed", "cancelled"}:
            return final
    raise TimeoutError(f"{workflow_id} timed out run_id={run_id}")


def start_or_resume(workflow_id: str, transcript_id: str, resume_id: str | None) -> str:
    if resume_id:
        print(f"\n== resume {workflow_id} run_id={resume_id} ==")
        return resume_id
    print(f"\n== start {workflow_id} (background=true) ==")
    # POST can itself 504 if the API is busy — retry carefully.
    _, run = http_json(
        "POST",
        f"/api/workflows/{workflow_id}/run",
        {"transcript_id": transcript_id, "background": True},
        timeout=60,
    )
    run_id = run["id"]
    print(f"queued run_id={run_id} initial_status={run.get('status')}")
    return run_id


def main() -> int:
    print(f"ALB base: {BASE}", flush=True)
    _, health = http_json("GET", "/api/health")
    print(
        f"health: status={health.get('status')} "
        f"llm={health.get('llm_provider')}/{health.get('llm_available')} "
        f"asr={health.get('transcription_provider')}/{health.get('transcription_available')} "
        f"db={health.get('database_available')}",
        flush=True,
    )
    if health.get("status") != "ok" or not health.get("llm_available"):
        print("FAIL: API not healthy for Bedrock burn-in")
        return 1

    _, workflows = http_json("GET", "/api/workflows")
    ids = {w["id"] for w in workflows.get("workflows", [])}
    print(f"workflows ({len(ids)}): {sorted(ids)}")
    for required in ("research_oriented", "full_multidisciplinary"):
        if required not in ids:
            print(f"FAIL: missing workflow {required}")
            return 1

    if RESUME_TRANSCRIPT:
        transcript_id = RESUME_TRANSCRIPT
        print(f"reuse transcript_id={transcript_id}")
    else:
        text = FIXTURE.read_text(encoding="utf-8")
        _, created = http_json(
            "POST",
            "/api/transcripts",
            {
                "raw_text": text,
                "source_type": "paste",
                "title": "P1-4f burn-in golden",
            },
        )
        transcript_id = created["transcript"]["id"]
        print(f"ingest transcript_id={transcript_id}")
        _, ready = http_json(
            "POST",
            f"/api/transcripts/{transcript_id}/ready",
            {"skip_review": True},
        )
        print(
            f"marked ready analysis_ready={ready['transcript'].get('analysis_ready')} "
            f"skip_review={ready['transcript'].get('skip_review')}"
        )

    results: dict[str, str] = {}
    plan = (
        ("research_oriented", RESUME_RESEARCH, 6),
        ("full_multidisciplinary", RESUME_FULL, 13),
    )
    for workflow_id, resume_id, expected_modules in plan:
        run_id = start_or_resume(workflow_id, transcript_id, resume_id)
        try:
            final = poll_run(workflow_id, run_id)
        except TimeoutError as exc:
            print(f"FAIL: {exc}")
            return 1
        results[workflow_id] = final.get("status", "unknown")
        modules = final.get("module_runs") or []
        print(
            f"  final status={results[workflow_id]} "
            f"module_runs={len(modules)} "
            f"error={final.get('error_log')!r}"
        )
        if results[workflow_id] != "completed":
            print(f"FAIL: {workflow_id} did not complete")
            return 1
        if len(modules) != expected_modules:
            print(f"FAIL: expected {expected_modules} module runs, got {len(modules)}")
            return 1
        try:
            _, synth = http_json("GET", f"/api/workflow-runs/{run_id}/synthesis")
            findings = synth.get("findings") or []
            if not findings:
                # Backward-compatible count if an older image lacks the rollup field.
                findings = (
                    (synth.get("high_confidence_findings") or [])
                    + (synth.get("moderate_confidence_findings") or [])
                    + (synth.get("exploratory_hypotheses") or [])
                )
            print(
                f"  synthesis ok id={synth.get('id')} "
                f"findings={len(findings)} "
                f"high={len(synth.get('high_confidence_findings') or [])} "
                f"moderate={len(synth.get('moderate_confidence_findings') or [])} "
                f"exploratory={len(synth.get('exploratory_hypotheses') or [])}"
            )
            if not findings:
                print(f"FAIL: {workflow_id} synthesis returned zero findings")
                return 1
            if not (synth.get("executive_summary") or "").strip():
                print(f"FAIL: {workflow_id} synthesis missing executive_summary")
                return 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: synthesis check: {exc}")
            return 1
    print("\nP1-4f burn-in OK:", results)
    print(f"transcript_id={transcript_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
