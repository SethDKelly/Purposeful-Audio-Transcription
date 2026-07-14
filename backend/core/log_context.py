"""Request and run correlation IDs for structured logging."""

from __future__ import annotations

import contextvars
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
workflow_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "workflow_run_id", default=None
)
module_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "module_run_id", default=None
)
module_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "module_id", default=None
)


def log_context_extra(**overrides: Any) -> dict[str, Any]:
    """Build logging ``extra`` dict with standard correlation fields."""
    extra: dict[str, Any] = {}
    for key, var in (
        ("request_id", request_id_var),
        ("workflow_run_id", workflow_run_id_var),
        ("module_run_id", module_run_id_var),
        ("module_id", module_id_var),
    ):
        value = overrides.pop(key, None)
        if value is None:
            value = var.get()
        if value is not None:
            extra[key] = value
    extra.update(overrides)
    return extra
