"""Evaluation harness for golden fixtures and safety red-team scoring (v1.2)."""

from backend.evaluation.claims import ForbiddenClaimScorer, score_forbidden_claims
from backend.evaluation.harness import (
    EvalGateConfig,
    GoldenEvalHarness,
    ModuleVersionComparer,
    evaluate_module_output,
)
from backend.evaluation.reports import write_eval_reports

__all__ = [
    "EvalGateConfig",
    "ForbiddenClaimScorer",
    "GoldenEvalHarness",
    "ModuleVersionComparer",
    "evaluate_module_output",
    "score_forbidden_claims",
    "write_eval_reports",
]
