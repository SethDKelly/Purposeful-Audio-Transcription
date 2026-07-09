from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.services.audio_transcription_service import audio_transcription_service
from backend.services.diarization_service import SpeakerInterval
from backend.services.whisper_service import TranscriptResult, TranscriptSegment


@patch("backend.services.audio_transcription_service.settings")
@patch("backend.services.audio_transcription_service.diarization_service")
@patch("backend.services.audio_transcription_service.whisper_service")
def test_transcribe_applies_diarization_when_available(
    mock_whisper: MagicMock,
    mock_diarization: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_settings.diarization_speaker_prefix = "Person"
    mock_diarization.is_available.return_value = True
    mock_diarization.diarize.return_value = [
        SpeakerInterval(speaker="SPEAKER_00", start=0.0, end=2.0),
        SpeakerInterval(speaker="SPEAKER_01", start=2.0, end=4.0),
    ]
    mock_whisper.transcribe.return_value = TranscriptResult(
        text="Hello. Hi.",
        segments=[
            TranscriptSegment(start=0.0, end=1.5, text="Hello."),
            TranscriptSegment(start=2.0, end=3.5, text="Hi."),
        ],
        language="en",
        duration_seconds=4.0,
    )

    result = audio_transcription_service.transcribe(Path("sample.wav"))

    assert result.diarization_applied is True
    assert result.speaker_count == 2
    assert "Person A: Hello." in result.text
    assert "Person B: Hi." in result.text


@patch("backend.services.audio_transcription_service.settings")
@patch("backend.services.audio_transcription_service.diarization_service")
@patch("backend.services.audio_transcription_service.whisper_service")
def test_transcribe_falls_back_when_diarization_unavailable(
    mock_whisper: MagicMock,
    mock_diarization: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_diarization.is_available.return_value = False
    mock_whisper.transcribe.return_value = TranscriptResult(
        text="Hello. Hi.",
        segments=[TranscriptSegment(start=0.0, end=3.0, text="Hello. Hi.")],
        language="en",
        duration_seconds=3.0,
    )

    result = audio_transcription_service.transcribe(Path("sample.wav"))

    assert result.diarization_applied is False
    assert result.speaker_count == 1
    assert result.text == "Hello. Hi."
    mock_diarization.diarize.assert_not_called()


@patch("backend.api.routes.transcribe.audio_transcription_service")
def test_transcribe_endpoint_returns_speaker_metadata(mock_service: MagicMock) -> None:
    from fastapi.testclient import TestClient

    from backend.main import app
    from backend.services.audio_transcription_service import AudioTranscriptionResult

    mock_service.transcribe.return_value = AudioTranscriptionResult(
        text="Person A: Hello.\nPerson B: Hi.",
        segments=[TranscriptSegment(start=0.0, end=1.0, text="Hello.")],
        language="en",
        duration_seconds=2.0,
        speaker_count=2,
        speaker_labels=["Person A", "Person B"],
        diarization_applied=True,
    )

    client = TestClient(app)
    response = client.post(
        "/api/transcribe",
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["speaker_count"] == 2
    assert payload["diarization_applied"] is True
    assert payload["speaker_labels"] == ["Person A", "Person B"]
