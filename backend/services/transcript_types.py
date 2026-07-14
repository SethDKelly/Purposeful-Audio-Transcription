"""Shared ASR segment types (safe to import without faster-whisper / torch)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TaggedSegment:
    segment: TranscriptSegment
    speaker: str


@dataclass
class TranscriptResult:
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str | None = None
    duration_seconds: float | None = None
    tagged_segments: list[TaggedSegment] = field(default_factory=list)
