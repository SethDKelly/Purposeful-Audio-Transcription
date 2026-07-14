import logging
import shutil
import subprocess
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from config.settings import settings
from backend.core.exceptions import AudioValidationError

logger = logging.getLogger(__name__)


def check_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def check_ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def load_waveform_for_diarization(audio_path: Path) -> dict:
    """Decode audio via ffmpeg for pyannote when torchcodec is unavailable."""
    import json

    import torch

    if not check_ffmpeg_available() or not check_ffprobe_available():
        raise RuntimeError("ffmpeg and ffprobe are required for speaker diarization")

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate,channels",
            "-of",
            "json",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    stream = json.loads(probe.stdout)["streams"][0]
    sample_rate = int(stream["sample_rate"])
    channels = int(stream.get("channels", 1))

    decode = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(audio_path),
            "-f",
            "f32le",
            "-acodec",
            "pcm_f32le",
            "-ac",
            str(channels),
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    if not decode.stdout:
        raise RuntimeError(f"No audio decoded from {audio_path.name}")

    waveform = torch.frombuffer(bytearray(decode.stdout), dtype=torch.float32).reshape(
        channels, -1
    )
    return {"waveform": waveform, "sample_rate": sample_rate}


def validate_audio_file(filename: str, size_bytes: int) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise AudioValidationError(
            f"Unsupported file type '{suffix}'. "
            f"Allowed: {', '.join(sorted(settings.allowed_extensions))}"
        )
    if size_bytes > settings.max_upload_bytes:
        raise AudioValidationError(
            f"File exceeds maximum size of {settings.max_upload_mb} MB"
        )
    if size_bytes == 0:
        raise AudioValidationError("Uploaded file is empty")


@contextmanager
def saved_upload(content: bytes, original_filename: str) -> Generator[Path, None, None]:
    """Write upload bytes to a temp file and delete on exit."""
    validate_audio_file(original_filename, len(content))

    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(original_filename).suffix.lower()
    temp_path = settings.temp_dir / f"{uuid.uuid4()}{suffix}"

    try:
        temp_path.write_bytes(content)
        logger.debug("Saved upload to %s (%d bytes)", temp_path, len(content))
        yield temp_path
    finally:
        if temp_path.exists():
            temp_path.unlink()
            logger.debug("Removed temp file %s", temp_path)
