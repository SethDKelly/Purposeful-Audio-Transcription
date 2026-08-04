"""Helpers for selecting workflow runs from ordered lists."""

from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


def select_latest_completed_run(runs: list[T]) -> T | None:
    """Return the newest completed run.

    ``list_by_transcript_id`` / ``list_transcript_workflow_runs`` order by
    ``started_at`` descending, so the first completed entry is the latest.
    """
    for run in runs:
        status = _run_status(run)
        if status == "completed":
            return run
    return None


def _run_status(run: Any) -> str:
    if isinstance(run, dict):
        return str(run.get("status") or "").lower()
    return str(getattr(run, "status", "") or "").lower()
