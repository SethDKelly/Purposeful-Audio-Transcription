"""Whisper + optional pyannote path wrapped as a TranscriptionProvider."""

from __future__ import annotations

from pathlib import Path

from backend.services.audio_transcription_service import (
    AudioTranscriptionResult,
    AudioTranscriptionService,
    audio_transcription_service,
)
from backend.services.whisper_service import whisper_service


class WhisperTranscriptionProvider:
    name = "whisper"

    def __init__(self, service: AudioTranscriptionService | None = None) -> None:
        self._service = service or audio_transcription_service

    def health_check(self) -> bool:
        return whisper_service.is_ready()

    def transcribe(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None = None,
    ) -> AudioTranscriptionResult:
        return self._service.transcribe(audio_path, num_speakers=num_speakers)
