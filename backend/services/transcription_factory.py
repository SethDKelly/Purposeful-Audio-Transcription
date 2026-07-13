"""Resolve the active transcription provider from settings."""

from __future__ import annotations

from backend.services.transcription_provider import TranscriptionProvider
from config.settings import settings

_provider: TranscriptionProvider | None = None


def get_transcription_provider() -> TranscriptionProvider:
    global _provider
    if _provider is not None:
        return _provider

    name = settings.transcription_provider.strip().lower()
    if name in {"transcribe", "amazon_transcribe", "aws_transcribe"}:
        from backend.services.amazon_transcribe_provider import AmazonTranscribeProvider

        _provider = AmazonTranscribeProvider()
    else:
        from backend.services.whisper_transcription_provider import (
            WhisperTranscriptionProvider,
        )

        _provider = WhisperTranscriptionProvider()
    return _provider


def reset_transcription_provider() -> None:
    """Clear cached provider (tests)."""
    global _provider
    _provider = None
