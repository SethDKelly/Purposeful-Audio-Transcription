from unittest.mock import MagicMock, patch

from backend.core.device import (
    resolve_torch_device,
    resolve_whisper_compute_type,
    resolve_whisper_device,
)


@patch("backend.core.device.mps_available", return_value=False)
@patch("backend.core.device.cuda_available", return_value=True)
def test_resolve_torch_device_auto_prefers_cuda(
    _cuda: MagicMock,
    _mps: MagicMock,
) -> None:
    assert resolve_torch_device("auto") == "cuda"


@patch("backend.core.device.mps_available", return_value=True)
@patch("backend.core.device.cuda_available", return_value=False)
def test_resolve_torch_device_auto_falls_back_to_mps(
    _cuda: MagicMock,
    _mps: MagicMock,
) -> None:
    assert resolve_torch_device("auto") == "mps"


@patch("backend.core.device.mps_available", return_value=False)
@patch("backend.core.device.cuda_available", return_value=False)
def test_resolve_torch_device_auto_falls_back_to_cpu(
    _cuda: MagicMock,
    _mps: MagicMock,
) -> None:
    assert resolve_torch_device("auto") == "cpu"


@patch("backend.core.device.cuda_available", return_value=False)
def test_resolve_torch_device_cuda_falls_back_when_unavailable(_cuda: MagicMock) -> None:
    assert resolve_torch_device("cuda") == "cpu"


@patch("backend.core.device.mps_available", return_value=True)
@patch("backend.core.device.cuda_available", return_value=False)
def test_resolve_whisper_device_maps_mps_to_cpu(
    _cuda: MagicMock,
    _mps: MagicMock,
) -> None:
    assert resolve_whisper_device("auto") == "cpu"


def test_resolve_whisper_compute_type_promotes_int8_on_cuda() -> None:
    assert resolve_whisper_compute_type("cuda", "int8") == "float16"


def test_resolve_whisper_compute_type_honors_explicit_cuda_value() -> None:
    assert resolve_whisper_compute_type("cuda", "int8_float16") == "int8_float16"


def test_resolve_whisper_compute_type_demotes_float16_on_cpu() -> None:
    assert resolve_whisper_compute_type("cpu", "float16") == "int8"
