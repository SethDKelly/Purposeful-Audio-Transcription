"""Structured audit events (IDs and enums only — no transcript bodies)."""

from __future__ import annotations

import logging
from typing import Any

from backend.core.log_context import log_context_extra
from backend.core.log_sanitize import safe_extra

logger = logging.getLogger("rre.audit")


def audit_event(event: str, **fields: Any) -> None:
    """Emit an audit log line with correlation + allowlisted fields."""
    extra = log_context_extra(event=event, **safe_extra(**fields))
    logger.info(event, extra=extra)
