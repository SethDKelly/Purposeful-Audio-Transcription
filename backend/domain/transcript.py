from datetime import datetime

from pydantic import BaseModel, Field

from backend.domain.enums import SourceType


class Transcript(BaseModel):
    id: str
    title: str
    raw_text: str
    source_type: SourceType
    language: str | None = None
    created_at: datetime


class Speaker(BaseModel):
    id: str
    transcript_id: str
    label: str
    display_name: str | None = None


class Turn(BaseModel):
    id: str
    transcript_id: str
    speaker_id: str
    turn_index: int
    text: str
    start_time: str | None = None
    end_time: str | None = None


class EvidenceQuote(BaseModel):
    id: str
    transcript_id: str
    turn_id: str
    speaker_id: str
    quote_index: int
    quote_id: str
    text: str
    context_before: str | None = None
    context_after: str | None = None


class TranscriptBundle(BaseModel):
    transcript: Transcript
    speakers: list[Speaker] = Field(default_factory=list)
    turns: list[Turn] = Field(default_factory=list)
    evidence_quotes: list[EvidenceQuote] = Field(default_factory=list)
