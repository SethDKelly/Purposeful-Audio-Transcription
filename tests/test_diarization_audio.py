import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import torch

from backend.services.audio_service import load_waveform_for_diarization
from backend.services.diarization_service import DiarizationService, diarization_speaker_kwargs


@patch("backend.services.audio_service.subprocess.run")
def test_load_waveform_for_diarization_decodes_via_ffmpeg(mock_run: MagicMock) -> None:
    mock_run.side_effect = [
        MagicMock(
            stdout=json.dumps({"streams": [{"sample_rate": "16000", "channels": "1"}]}),
            returncode=0,
        ),
        MagicMock(stdout=(torch.zeros(1600, dtype=torch.float32).numpy().tobytes()), returncode=0),
    ]

    result = load_waveform_for_diarization(Path("sample.wav"))

    assert result["sample_rate"] == 16000
    assert result["waveform"].shape == (1, 1600)
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[1].args[0][0] == "ffmpeg"


@patch("backend.services.diarization_service.settings")
@patch("backend.services.diarization_service.load_waveform_for_diarization")
def test_diarize_passes_waveform_dict_to_pipeline(
    mock_load_waveform: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_min_speakers = None
    mock_settings.diarization_max_speakers = None

    waveform = {"waveform": torch.zeros(1, 100), "sample_rate": 16000}
    mock_load_waveform.return_value = waveform

    mock_annotation = MagicMock()
    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 1.0
    mock_annotation.itertracks.return_value = [(mock_segment, None, "SPEAKER_00")]

    mock_pipeline = MagicMock(return_value=mock_annotation)

    service = DiarizationService()
    with (
        patch.object(service, "is_available", return_value=True),
        patch.object(service, "_get_pipeline", return_value=mock_pipeline),
    ):
        intervals = service.diarize(Path("sample.wav"))

    mock_load_waveform.assert_called_once_with(Path("sample.wav"))
    mock_pipeline.assert_called_once_with(waveform)
    assert len(intervals) == 1
    assert intervals[0].speaker == "SPEAKER_00"


@patch("backend.services.diarization_service.settings")
def test_diarization_speaker_kwargs_prefers_request_hint(mock_settings: MagicMock) -> None:
    mock_settings.diarization_min_speakers = 1
    mock_settings.diarization_max_speakers = 6

    assert diarization_speaker_kwargs(2) == {"min_speakers": 2, "max_speakers": 2}


@patch("backend.services.diarization_service.settings")
def test_diarization_speaker_kwargs_uses_settings_when_no_hint(mock_settings: MagicMock) -> None:
    mock_settings.diarization_min_speakers = 2
    mock_settings.diarization_max_speakers = 4

    assert diarization_speaker_kwargs(None) == {"min_speakers": 2, "max_speakers": 4}


@patch("backend.services.diarization_service.settings")
@patch("backend.services.diarization_service.load_waveform_for_diarization")
def test_diarize_passes_speaker_hint_to_pipeline(
    mock_load_waveform: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_min_speakers = None
    mock_settings.diarization_max_speakers = None

    waveform = {"waveform": torch.zeros(1, 100), "sample_rate": 16000}
    mock_load_waveform.return_value = waveform

    mock_annotation = MagicMock()
    mock_annotation.itertracks.return_value = []

    mock_pipeline = MagicMock(return_value=mock_annotation)

    service = DiarizationService()
    with (
        patch.object(service, "is_available", return_value=True),
        patch.object(service, "_get_pipeline", return_value=mock_pipeline),
    ):
        service.diarize(Path("sample.wav"), num_speakers=2)

    mock_pipeline.assert_called_once_with(
        waveform,
        min_speakers=2,
        max_speakers=2,
    )
