"""Assess transcript evidence length and prompt truncation strategy (v1.0 P4)."""

from __future__ import annotations

from pydantic import BaseModel

from backend.services.evidence_index import STRATEGY_FULL, EvidenceIndexService
from backend.services.transcript_service import TranscriptService, transcript_service
from config.settings import settings


class LengthAssessment(BaseModel):
    quote_count: int
    max_quotes: int
    strategy: str
    warning: str | None = None
    omitted_quotes: int = 0


class TranscriptLengthService:
    def __init__(
        self,
        transcripts: TranscriptService | None = None,
        evidence_index: EvidenceIndexService | None = None,
    ) -> None:
        self._transcripts = transcripts or transcript_service
        self._evidence_index = evidence_index or EvidenceIndexService()

    def assess_transcript(self, transcript_id: str) -> LengthAssessment:
        bundle = self._transcripts.get(transcript_id)
        return self.assess_quotes(bundle.evidence_quotes)

    def assess_quotes(self, quotes: list) -> LengthAssessment:
        quote_count = len(quotes)
        max_quotes = settings.evidence_prompt_max_quotes
        if quote_count <= max_quotes:
            return LengthAssessment(
                quote_count=quote_count,
                max_quotes=max_quotes,
                strategy=STRATEGY_FULL,
            )

        _, note, strategy = self._evidence_index.select_quotes_for_prompt(quotes)
        omitted = quote_count - max_quotes
        warning = (
            f"Transcript has {quote_count} evidence quotes; module prompts include "
            f"{max_quotes} using strategy={strategy}. "
            f"{omitted} quotes are omitted from prompts (full index retained in database)."
        )
        if note:
            warning = f"{warning} {note}"
        return LengthAssessment(
            quote_count=quote_count,
            max_quotes=max_quotes,
            strategy=strategy,
            warning=warning,
            omitted_quotes=omitted,
        )


transcript_length_service = TranscriptLengthService()
