"""Ownership helpers for `/api/v1` product routes."""

from __future__ import annotations

from backend.api.deps import AuthContext, assert_resource_owner
from backend.db.base import get_session
from backend.db.models import CaseRow, TranscriptRow, WorkflowRunRow
from backend.core.exceptions import (
    CaseNotFoundError,
    TranscriptNotFoundError,
    WorkflowRunNotFoundError,
)


def transcript_owner_id(transcript_id: str) -> str | None:
    with get_session() as session:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        return row.owner_user_id


def case_owner_id(case_id: str) -> str | None:
    with get_session() as session:
        row = session.get(CaseRow, case_id)
        if row is None:
            raise CaseNotFoundError(f"Case not found: {case_id}")
        return row.owner_user_id


def workflow_run_owner_id(run_id: str) -> str | None:
    with get_session() as session:
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            raise WorkflowRunNotFoundError(f"Workflow run not found: {run_id}")
        return row.owner_user_id


def assert_transcript_access(transcript_id: str, ctx: AuthContext) -> None:
    assert_resource_owner(transcript_owner_id(transcript_id), ctx)


def assert_case_access(case_id: str, ctx: AuthContext) -> None:
    assert_resource_owner(case_owner_id(case_id), ctx)


def assert_run_access(run_id: str, ctx: AuthContext) -> None:
    assert_resource_owner(workflow_run_owner_id(run_id), ctx)
