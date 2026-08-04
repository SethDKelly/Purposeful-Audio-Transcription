#!/usr/bin/env python3
"""Run golden evaluation scoring against mocked module outputs.

Examples:
  python scripts/run_golden_eval.py
  python scripts/run_golden_eval.py --fixture GT001 --module relationship_conversation_analysis
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Isolate DB before importing backend settings/engine.
_EVAL_DB = Path(tempfile.gettempdir()) / "purposeful_rre_golden_eval.db"
if _EVAL_DB.exists():
    _EVAL_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_EVAL_DB.as_posix()}"
os.environ["ALEMBIC_AUTO_UPGRADE"] = "false"
os.environ["API_KEY"] = ""
os.environ["AUTO_MARK_TRANSCRIPT_READY"] = "true"
os.environ["LLM_PROVIDER"] = "bedrock"  # factory still mocked below

from backend.core.module_registry import ModuleRegistry
from backend.db.base import Base, engine, init_db
from backend.domain.enums import SourceType
from backend.evaluation.harness import (
    DEFAULT_RESULTS_DIR,
    EvalGateConfig,
    GoldenEvalHarness,
    ModuleVersionComparer,
)
from backend.evaluation.reports import write_eval_reports
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import transcript_service
from tests.helpers.golden_transcripts import iter_golden_fixtures, load_golden_fixture_by_id
from tests.test_workflow_engine import _module_llm_response


def _parse_module_response(module_id: str) -> dict:
    raw = _module_llm_response(module_id)
    payload = raw.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
    return json.loads(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Golden evaluation harness")
    parser.add_argument("--fixture", action="append", dest="fixtures", help="Fixture ID (repeatable)")
    parser.add_argument("--module", action="append", dest="modules", help="Module ID (repeatable)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / DEFAULT_RESULTS_DIR,
        help="Where to write JSON/Markdown reports",
    )
    parser.add_argument(
        "--compare-versions",
        action="store_true",
        help="Emit baseline vs candidate comparison scaffold",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Score canned mock JSON only (skip ModuleRunner ingest path)",
    )
    args = parser.parse_args()

    Base.metadata.drop_all(bind=engine)
    init_db()

    fixtures = (
        [load_golden_fixture_by_id(fid) for fid in args.fixtures]
        if args.fixtures
        else iter_golden_fixtures()
    )
    modules = args.modules or [
        "relationship_conversation_analysis",
        "nvc_analysis",
        "bias_epistemic_quality",
    ]

    harness = GoldenEvalHarness(
        EvalGateConfig(min_required_signal_hit_rate=0.0, min_evidence_coverage_rate=0.0)
    )
    registry = ModuleRegistry()
    results = []
    comparisons = []

    for fixture in fixtures:
        quote_ids: set[str] | None = None
        transcript_id: str | None = None
        if not args.offline:
            bundle = transcript_service.ingest(
                raw_text=fixture.labeled_text(),
                source_type=SourceType.PASTE,
                title=fixture.fixture_id,
            )
            transcript_service.mark_ready(bundle.transcript.id, skip_review=True)
            quote_ids = {q.quote_id for q in bundle.evidence_quotes}
            transcript_id = bundle.transcript.id

        for module_id in modules:
            cfg = registry.get(module_id)
            canned = _parse_module_response(module_id)
            output = canned
            version = getattr(cfg, "version", None)
            if transcript_id and not args.offline:
                mock_llm = MagicMock()
                mock_llm.chat.return_value = _module_llm_response(module_id)
                mock_llm.chat_cached.side_effect = (
                    lambda *a, **k: _module_llm_response(module_id)
                )
                runner = ModuleRunner(
                    registry=registry,
                    llm=mock_llm,
                    transcripts=transcript_service,
                )
                run = runner.run(
                    module_id=module_id,
                    transcript_id=transcript_id,
                    model="mock-eval",
                )
                output = run.parsed_output or canned
                version = run.module_version or version

            scored = harness.score_output(
                fixture_id=fixture.fixture_id,
                module_id=module_id,
                module_output=output,
                valid_quote_ids=quote_ids,
                confidence_ceiling=str(getattr(cfg, "confidence_ceiling", "") or "") or None,
                module_version=version,
                model_id="mock-eval",
                workflow_id="quick_review",
            )
            results.append(scored)

            if args.compare_versions:
                candidate_output = dict(output)
                candidate = harness.score_output(
                    fixture_id=fixture.fixture_id,
                    module_id=module_id,
                    module_output=candidate_output,
                    valid_quote_ids=quote_ids,
                    confidence_ceiling=str(getattr(cfg, "confidence_ceiling", "") or "")
                    or None,
                    module_version=f"{version or '0'}-candidate",
                    model_id="mock-eval",
                    workflow_id="quick_review",
                )
                comparisons.append(
                    ModuleVersionComparer().compare(baseline=scored, candidate=candidate)
                )

    paths = write_eval_reports(results, args.output_dir, comparisons=comparisons)
    failed = [r for r in results if not r.gate_passed]
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['markdown']}")
    print(f"Results: {len(results)}; gate failures: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
