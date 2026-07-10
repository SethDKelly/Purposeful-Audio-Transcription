import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import torch

from backend.services.audio_service import load_waveform_for_diarization
from backend.services.diarization_service import (
    DiarizationService,
    annotation_from_pipeline_output,
    diarization_speaker_kwargs,
)


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
    mock_settings.diarization_min_duration_on = 0.0
    mock_settings.diarization_min_duration_off = 0.0

    waveform = {"waveform": torch.zeros(1, 100), "sample_rate": 16000}
    mock_load_waveform.return_value = waveform

    mock_annotation = MagicMock(spec=["itertracks"])
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

    assert diarization_speaker_kwargs(2) == {"num_speakers": 2}


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
    mock_settings.diarization_min_duration_on = 0.0
    mock_settings.diarization_min_duration_off = 0.0

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
        num_speakers=2,
    )


def test_annotation_from_pipeline_output_prefers_exclusive() -> None:
    exclusive = MagicMock(name="exclusive")
    regular = MagicMock(name="regular")
    output = MagicMock()
    output.exclusive_speaker_diarization = exclusive
    output.speaker_diarization = regular

    assert annotation_from_pipeline_output(output) is exclusive


def test_annotation_from_pipeline_output_falls_back_to_speaker_diarization() -> None:
    regular = MagicMock(name="regular")
    output = MagicMock(spec=["speaker_diarization"])
    output.speaker_diarization = regular

    assert annotation_from_pipeline_output(output) is regular


def test_annotation_from_pipeline_output_accepts_legacy_annotation() -> None:
    annotation = MagicMock(spec=["itertracks"])
    assert annotation_from_pipeline_output(annotation) is annotation


@patch("backend.services.diarization_service.settings")
@patch("backend.services.diarization_service.load_waveform_for_diarization")
def test_diarize_unwraps_diarize_output(
    mock_load_waveform: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_min_speakers = None
    mock_settings.diarization_max_speakers = None
    mock_settings.diarization_min_duration_on = 0.0
    mock_settings.diarization_min_duration_off = 0.0

    waveform = {"waveform": torch.zeros(1, 100), "sample_rate": 16000}
    mock_load_waveform.return_value = waveform

    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 1.5
    annotation = MagicMock()
    annotation.itertracks.return_value = [(mock_segment, None, "SPEAKER_00")]

    diarize_output = MagicMock()
    diarize_output.exclusive_speaker_diarization = annotation
    diarize_output.speaker_diarization = MagicMock()

    mock_pipeline = MagicMock(return_value=diarize_output)

    service = DiarizationService()
    with (
        patch.object(service, "is_available", return_value=True),
        patch.object(service, "_get_pipeline", return_value=mock_pipeline),
    ):
        intervals = service.diarize(Path("sample.wav"), num_speakers=2)

    assert len(intervals) == 1
    assert intervals[0].speaker == "SPEAKER_00"
    assert intervals[0].end == 1.5


@patch("backend.services.diarization_service.settings")
def test_get_pipeline_moves_to_cuda_when_resolved(mock_settings: MagicMock) -> None:
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_device = "auto"

    mock_pipeline = MagicMock()

    with (
        patch(
            "backend.services.diarization_service.resolve_torch_device",
            return_value="cuda",
        ),
        patch("pyannote.audio.Pipeline") as mock_pipeline_cls,
        patch("torch.device", side_effect=lambda name: f"device:{name}"),
    ):
        mock_pipeline_cls.from_pretrained.return_value = mock_pipeline
        service = DiarizationService()
        loaded = service._get_pipeline()

    assert loaded is mock_pipeline
    mock_pipeline.to.assert_called_once_with("device:cuda")
    assert service.resolved_device() == "cuda"


@patch("backend.services.diarization_service.settings")
def test_get_pipeline_skips_to_on_cpu(mock_settings: MagicMock) -> None:
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_device = "cpu"

    mock_pipeline = MagicMock()

    with (
        patch(
            "backend.services.diarization_service.resolve_torch_device",
            return_value="cpu",
        ),
        patch("pyannote.audio.Pipeline") as mock_pipeline_cls,
    ):
        mock_pipeline_cls.from_pretrained.return_value = mock_pipeline
        service = DiarizationService()
        service._get_pipeline()

    mock_pipeline.to.assert_not_called()
    assert service.resolved_device() == "cpu"


@patch("backend.services.diarization_service.settings")
@patch("backend.services.diarization_service.load_waveform_for_diarization")
def test_diarize_applies_timeline_smoothing(
    mock_load_waveform: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.diarization_enabled = True
    mock_settings.hf_token = "token"
    mock_settings.diarization_model = "pyannote/speaker-diarization-3.1"
    mock_settings.diarization_min_speakers = None
    mock_settings.diarization_max_speakers = None
    mock_settings.diarization_min_duration_on = 0.3
    mock_settings.diarization_min_duration_off = 0.2

    mock_load_waveform.return_value = {
        "waveform": torch.zeros(1, 100),
        "sample_rate": 16000,
    }

    def make_segment(start: float, end: float) -> MagicMock:
        segment = MagicMock()
        segment.start = start
        segment.end = end
        return segment

    mock_annotation = MagicMock(spec=["itertracks"])
    mock_annotation.itertracks.return_value = [
        (make_segment(0.0, 2.0), None, "SPEAKER_00"),
        (make_segment(2.05, 2.15), None, "SPEAKER_01"),
        (make_segment(2.18, 4.0), None, "SPEAKER_00"),
    ]
    mock_pipeline = MagicMock(return_value=mock_annotation)

    service = DiarizationService()
    with (
        patch.object(service, "is_available", return_value=True),
        patch.object(service, "_get_pipeline", return_value=mock_pipeline),
    ):
        intervals = service.diarize(Path("sample.wav"))

    assert len(intervals) == 1
    assert intervals[0].speaker == "SPEAKER_00"
    assert intervals[0].start == 0.0
    assert intervals[0].end == 4.0

