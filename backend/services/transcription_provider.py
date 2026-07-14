"""Transcription provider protocol — Whisper (local) and Transcribe (AWS, P1-1)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.services.audio_transcription_service import AudioTranscriptionResult


class TranscriptionProvider(Protocol):
    @property
    def name(self) -> str: ...

    def health_check(self) -> bool: ...

    def transcribe(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None = None,
    ) -> AudioTranscriptionResult: ...
