"""Tests for Amazon Transcribe provider mapping and factory."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.core.exceptions import AudioValidationError
from backend.services.amazon_transcribe_provider import (
    AmazonTranscribeProvider,
    _result_from_transcribe_json,
)
from backend.services.transcript_types import AudioTranscriptionResult
from backend.services.transcription_factory import (
    get_transcription_provider,
    reset_transcription_provider,
)


@pytest.fixture(autouse=True)
def _reset_provider():
    reset_transcription_provider()
    yield
    reset_transcription_provider()


def test_factory_defaults_to_transcribe() -> None:
    provider = get_transcription_provider()
    assert isinstance(provider, AmazonTranscribeProvider)
    assert provider.name == "transcribe"


def test_transcribe_json_maps_speakers_to_person_labels() -> None:
    payload = {
        "results": {
            "transcripts": [{"transcript": "Hello Hi there"}],
            "language_code": "en-US",
            "items": [
                {
                    "type": "pronunciation",
                    "start_time": "0.0",
                    "end_time": "0.4",
                    "alternatives": [{"content": "Hello"}],
                    "speaker_label": "spk_0",
                },
                {
                    "type": "pronunciation",
                    "start_time": "0.5",
                    "end_time": "0.8",
                    "alternatives": [{"content": "Hi"}],
                    "speaker_label": "spk_1",
                },
                {
                    "type": "pronunciation",
                    "start_time": "0.9",
                    "end_time": "1.2",
                    "alternatives": [{"content": "there"}],
                    "speaker_label": "spk_1",
                },
            ],
        }
    }
    result = _result_from_transcribe_json(payload, speaker_prefix="Person")
    assert isinstance(result, AudioTranscriptionResult)
    assert "Person A:" in result.text
    assert "Person B:" in result.text
    assert result.speaker_count >= 2
    assert result.diarization_applied is True


def test_transcribe_requires_bucket(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.uploads_bucket",
        "",
    )
    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"RIFF")
    provider = AmazonTranscribeProvider()
    with pytest.raises(AudioValidationError, match="UPLOADS_BUCKET"):
        provider.transcribe(audio)


def test_transcribe_deletes_s3_objects(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.uploads_bucket",
        "bucket",
    )
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.transcribe_poll_seconds",
        0.01,
    )
    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"RIFF....")

    s3 = MagicMock()
    transcribe = MagicMock()
    transcribe.start_transcription_job.return_value = {}
    transcribe.get_transcription_job.return_value = {
        "TranscriptionJob": {
            "TranscriptionJobStatus": "COMPLETED",
            "Transcript": {"TranscriptFileUri": "s3://bucket/out.json"},
        }
    }
    payload = {
        "results": {
            "transcripts": [{"transcript": "Hello"}],
            "language_code": "en-US",
            "items": [
                {
                    "type": "pronunciation",
                    "start_time": "0.0",
                    "end_time": "0.4",
                    "alternatives": [{"content": "Hello"}],
                    "speaker_label": "spk_0",
                }
            ],
        }
    }
    s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: __import__("json").dumps(payload).encode())
    }

    with patch("backend.services.amazon_transcribe_provider.boto3.client") as client_factory:
        def _client(name, **_kwargs):
            return s3 if name == "s3" else transcribe

        client_factory.side_effect = _client
        provider = AmazonTranscribeProvider()
        result = provider.transcribe(audio)

    assert "Hello" in result.text
    assert s3.delete_object.call_count >= 1
