"""Helpers for concise evidence spans (phase 004)."""

from __future__ import annotations

import re

from config.settings import settings

EVIDENCE_TYPE_ATOMIC = "atomic_quote"
EVIDENCE_TYPE_SHORT_EXCHANGE = "short_exchange"
EVIDENCE_TYPE_CONTEXT_WINDOW = "context_window"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def extract_primary_span(text: str) -> str | None:
    """Return a shorter display span when the full turn is long.

    Keeps full ``text`` for transcript identity; UI shows this by default.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    if not settings.evidence_prefer_sentence_spans:
        return None
    if len(cleaned) <= settings.evidence_atomic_quote_max_chars:
        return None
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(cleaned) if p.strip()]
    if not parts:
        return None
    primary = parts[0]
    if len(primary) > settings.evidence_atomic_quote_max_chars:
        primary = primary[: settings.evidence_atomic_quote_max_chars - 3] + "..."
    if primary == cleaned:
        return None
    return primary


def classify_evidence_type(text: str, *, quote_count: int = 1) -> str:
    """Classify a cite or cite-set for storage / UI badges."""
    if quote_count > 1:
        if quote_count <= settings.evidence_short_exchange_max_turns:
            return EVIDENCE_TYPE_SHORT_EXCHANGE
        return EVIDENCE_TYPE_CONTEXT_WINDOW
    cleaned = (text or "").strip()
    if looks_like_paragraph(cleaned):
        return EVIDENCE_TYPE_CONTEXT_WINDOW
    return EVIDENCE_TYPE_ATOMIC


def looks_like_paragraph(text: str) -> bool:
    cleaned = (text or "").strip()
    if not cleaned:
        return False
    if settings.evidence_allow_paragraph_evidence:
        return False
    sentence_count = len([p for p in _SENTENCE_SPLIT.split(cleaned) if p.strip()])
    if "\n" in cleaned and len(cleaned) > settings.evidence_atomic_quote_max_chars:
        return True
    return (
        sentence_count >= 3
        and len(cleaned) > settings.evidence_atomic_quote_max_chars
    )


def display_text_for_quote(text: str, span_text: str | None = None) -> str:
    """Concise text for default UI / report inline display."""
    if span_text and span_text.strip():
        return span_text.strip()
    cleaned = (text or "").strip()
    if len(cleaned) <= settings.evidence_warning_threshold_chars:
        return cleaned
    primary = extract_primary_span(cleaned)
    if primary:
        return primary
    return cleaned[: settings.evidence_warning_threshold_chars - 3] + "..."
