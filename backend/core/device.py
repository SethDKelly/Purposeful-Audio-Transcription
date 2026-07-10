"""Shared accelerator device resolution for Whisper and diarization."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except ImportError:
        return False


def mps_available() -> bool:
    try:
        import torch

        return bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
    except ImportError:
        return False


def resolve_torch_device(preference: str = "auto") -> str:
    """Resolve a torch device string: cuda | mps | cpu.

    Preference may be auto, cuda, mps, or cpu. Invalid or unavailable
    preferences fall back toward CPU.
    """
    pref = (preference or "auto").strip().lower()
    if pref not in {"auto", "cuda", "mps", "cpu"}:
        logger.warning("Unknown device preference %r; using auto", preference)
        pref = "auto"

    if pref == "cpu":
        return "cpu"
    if pref == "cuda":
        return "cuda" if cuda_available() else "cpu"
    if pref == "mps":
        return "mps" if mps_available() else "cpu"

    # auto: CUDA → MPS → CPU
    if cuda_available():
        return "cuda"
    if mps_available():
        return "mps"
    return "cpu"


def resolve_whisper_device(preference: str = "auto") -> str:
    """Resolve a faster-whisper device (cuda or cpu; MPS not supported)."""
    device = resolve_torch_device(preference)
    if device == "mps":
        logger.info("MPS requested/detected for Whisper; falling back to CPU")
        return "cpu"
    return device


def resolve_whisper_compute_type(device: str, configured: str) -> str:
    """Pick a Whisper compute type appropriate for the resolved device.

    When the user leaves the default ``int8`` and CUDA is selected, prefer
    ``float16``. Explicit non-default values are honored, with a CPU safety
    fallback away from float16.
    """
    compute = (configured or "int8").strip().lower()
    if device == "cuda" and compute == "int8":
        return "float16"
    if device == "cpu" and compute == "float16":
        return "int8"
    return compute
