import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.exceptions import WhisperError
from backend.main import app
from backend.services.whisper_service import WhisperService


class _FakeSegment:
    def __init__(self, start: float, end: float, text: str) -> None:
        self.start = start
        self.end = end
        self.text = text


class _FakeInfo:
    duration = 10.0
    language = "en"


@patch.object(WhisperService, "_get_model")
def test_iter_transcription_events_yields_progress_and_result(mock_get_model: MagicMock) -> None:
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (
        iter(
            [
                _FakeSegment(0.0, 2.0, "Hello"),
                _FakeSegment(2.0, 5.0, "world"),
            ]
        ),
        _FakeInfo(),
    )
    mock_get_model.return_value = mock_model

    service = WhisperService()
    events = list(service.iter_transcription_events(Path("sample.wav")))

    assert [event["type"] for event in events] == [
        "started",
        "progress",
        "progress",
        "complete",
    ]
    assert events[0]["duration_seconds"] == 10.0
    assert events[1]["progress_ratio"] == pytest.approx(0.2)
    assert events[2]["segment_index"] == 2
    assert events[-1]["result"]["transcript"] == "Hello world"
    assert len(events[-1]["result"]["segments"]) == 2


@patch.object(WhisperService, "_get_model")
def test_transcribe_raises_on_error_event(mock_get_model: MagicMock) -> None:
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("model failed")
    mock_get_model.return_value = mock_model

    service = WhisperService()
    with pytest.raises(WhisperError, match="model failed"):
        service.transcribe(Path("sample.wav"))


@patch("backend.api.routes.transcribe.whisper_service.iter_transcription_events")
def test_transcribe_stream_endpoint_returns_ndjson(mock_iter) -> None:
    mock_iter.return_value = iter(
        [
            {
                "type": "started",
                "elapsed_seconds": 0.0,
                "duration_seconds": 10.0,
            },
            {
                "type": "complete",
                "elapsed_seconds": 1.5,
                "result": {
                    "transcript": "Hello",
                    "segments": [{"start": 0.0, "end": 1.0, "text": "Hello"}],
                    "language": "en",
                    "duration_seconds": 10.0,
                },
            },
        ]
    )

    client = TestClient(app)
    response = client.post(
        "/api/transcribe/stream",
        files={"file": ("sample.wav", b"fake-audio", "audio/wav")},
    )

    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.strip().splitlines()]
    assert events[0]["type"] == "started"
    assert events[-1]["type"] == "complete"
    assert events[-1]["result"]["transcript"] == "Hello"
