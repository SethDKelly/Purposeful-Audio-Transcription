"""Tests for TranscriptionProvider factory and Amazon Transcribe mapping."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.core.exceptions import AudioValidationError
from backend.services.amazon_transcribe_provider import (
    AmazonTranscribeProvider,
    _result_from_transcribe_json,
)
from backend.services.audio_transcription_service import AudioTranscriptionResult
from backend.services.transcription_factory import (
    get_transcription_provider,
    reset_transcription_provider,
)
from backend.services.whisper_transcription_provider import WhisperTranscriptionProvider


@pytest.fixture(autouse=True)
def _reset_provider():
    reset_transcription_provider()
    yield
    reset_transcription_provider()


def test_whisper_provider_delegates_to_service(tmp_path: Path) -> None:
    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"fake")
    service = MagicMock()
    service.transcribe.return_value = AudioTranscriptionResult(
        text="Person A: Hello",
        speaker_count=1,
        transcription_mode="overlap",
    )
    provider = WhisperTranscriptionProvider(service=service)

    result = provider.transcribe(audio, num_speakers=2)

    assert provider.name == "whisper"
    assert result.text.startswith("Person A")
    service.transcribe.assert_called_once_with(audio, num_speakers=2)


def test_factory_defaults_to_whisper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.services.transcription_factory.settings.transcription_provider",
        "whisper",
    )
    provider = get_transcription_provider()
    assert isinstance(provider, WhisperTranscriptionProvider)


def test_factory_selects_transcribe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.services.transcription_factory.settings.transcription_provider",
        "transcribe",
    )
    provider = get_transcription_provider()
    assert isinstance(provider, AmazonTranscribeProvider)


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
    result = _result_from_transcribe_json(payload)
    assert "Person A: Hello" in result.text
    assert "Person B: Hi there" in result.text
    assert result.speaker_labels == ["Person A", "Person B"]
    assert result.speaker_count == 2
    assert result.diarization_applied is True
    assert result.transcription_mode == "transcribe"
    assert result.language == "en-US"


def test_transcribe_requires_uploads_bucket(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.uploads_bucket",
        "",
    )
    provider = AmazonTranscribeProvider()
    with pytest.raises(AudioValidationError, match="UPLOADS_BUCKET"):
        provider.transcribe(tmp_path / "x.wav")


def test_transcribe_rejects_unknown_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.uploads_bucket",
        "bucket",
    )
    audio = tmp_path / "clip.xyz"
    audio.write_bytes(b"x")
    provider = AmazonTranscribeProvider()
    with pytest.raises(AudioValidationError, match="Unsupported audio extension"):
        provider.transcribe(audio)


def test_transcribe_job_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.uploads_bucket",
        "rre-bucket",
    )
    monkeypatch.setattr(
        "backend.services.amazon_transcribe_provider.settings.transcribe_poll_seconds",
        0.01,
    )
    audio = tmp_path / "clip.wav"
    audio.write_bytes(b"RIFF")

    payload = {
        "results": {
            "transcripts": [{"transcript": "Hello"}],
            "items": [
                {
                    "type": "pronunciation",
                    "start_time": "0.0",
                    "end_time": "0.5",
                    "alternatives": [{"content": "Hello"}],
                    "speaker_label": "spk_0",
                }
            ],
        }
    }

    s3 = MagicMock()
    transcribe = MagicMock()
    transcribe.get_transcription_job.return_value = {
        "TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}
    }

    provider = AmazonTranscribeProvider()
    provider._s3 = s3
    provider._transcribe = transcribe
    provider._load_transcript_json = MagicMock(return_value=payload)  # type: ignore[method-assign]

    result = provider.transcribe(audio, num_speakers=2)

    assert result.text.startswith("Person A:")
    s3.upload_file.assert_called_once()
    transcribe.start_transcription_job.assert_called_once()
    start_kwargs = transcribe.start_transcription_job.call_args.kwargs
    assert start_kwargs["MediaFormat"] == "wav"
    assert start_kwargs["Settings"]["MaxSpeakerLabels"] == 2
    assert start_kwargs["OutputBucketName"] == "rre-bucket"
    assert s3.delete_object.call_count >= 1
