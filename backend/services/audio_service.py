import logging
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from backend.core.exceptions import AudioValidationError
from config.settings import settings

logger = logging.getLogger(__name__)


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
