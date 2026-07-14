"""Shared ASR types (safe to import without torch)."""

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


@dataclass
class AudioTranscriptionResult:
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str | None = None
    duration_seconds: float | None = None
    speaker_count: int = 1
    speaker_labels: list[str] = field(default_factory=list)
    diarization_applied: bool = False
    diarization_skip_reason: str | None = None
    transcription_mode: str = "transcribe"
