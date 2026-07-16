"""Resolve the active transcription provider (Amazon Transcribe only)."""

from __future__ import annotations

from backend.services.amazon_transcribe_provider import AmazonTranscribeProvider
from backend.services.transcription_provider import TranscriptionProvider

_provider: TranscriptionProvider | None = None


def get_transcription_provider() -> TranscriptionProvider:
    global _provider
    if _provider is not None:
        return _provider
    _provider = AmazonTranscribeProvider()
    return _provider


def reset_transcription_provider() -> None:
    """Clear cached provider (tests)."""
    global _provider
    _provider = None
