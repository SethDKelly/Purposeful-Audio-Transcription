"""Write Markdown/JSON evaluation reports outside fixture trees."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.evaluation.harness import ModuleEvalResult


def write_eval_reports(
    results: list[ModuleEvalResult],
    output_dir: Path,
    *,
    run_id: str | None = None,
    comparisons: list[dict[str, Any]] | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "run_id": stamp,
        "generated_at": datetime.now(UTC).isoformat(),
        "result_count": len(results),
        "gate_failures": [r.to_dict() for r in results if not r.gate_passed],
        "results": [r.to_dict() for r in results],
        "comparisons": comparisons or [],
    }
    json_path = output_dir / f"eval_{stamp}.json"
    md_path = output_dir / f"eval_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(payload), encoding="utf-8")
    latest = output_dir / "latest.json"
    latest.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    return {"json": json_path, "markdown": md_path, "latest": latest}


def _to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Golden eval report `{payload['run_id']}`",
        "",
        f"Generated: {payload['generated_at']}",
        f"Results: {payload['result_count']}",
        f"Gate failures: {len(payload['gate_failures'])}",
        "",
        "| Fixture | Module | Signals | Evidence | Forbidden | Gate |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in payload["results"]:
        lines.append(
            "| {fixture_id} | {module_id} | {required_signal_hit_rate:.2f} | "
            "{evidence_coverage_rate:.2f} | {forbidden_claim_count} | {gate} |".format(
                gate="PASS" if row["gate_passed"] else "FAIL",
                **row,
            )
        )
    if payload.get("comparisons"):
        lines.extend(["", "## Version comparisons", ""])
        for cmp in payload["comparisons"]:
            lines.append(
                f"- `{cmp.get('module_id')}` on `{cmp.get('fixture_id')}`: "
                f"regressions={cmp.get('regressions') or []}"
            )
    lines.append("")
    return "\n".join(lines)
