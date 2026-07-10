import logging
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from faster_whisper import WhisperModel

from backend.core.device import resolve_whisper_compute_type, resolve_whisper_device
from backend.core.exceptions import WhisperError
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str | None = None
    duration_seconds: float | None = None


class WhisperService:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None
        self._lock = Lock()
        self._resolved_device: str | None = None
        self._resolved_compute_type: str | None = None

    def resolved_device(self) -> str:
        """Device Whisper will use (or is using), without loading the model."""
        if self._resolved_device is not None:
            return self._resolved_device
        return resolve_whisper_device(settings.whisper_device)

    def resolved_compute_type(self) -> str:
        if self._resolved_compute_type is not None:
            return self._resolved_compute_type
        device = self.resolved_device()
        return resolve_whisper_compute_type(device, settings.whisper_compute_type)

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    device = resolve_whisper_device(settings.whisper_device)
                    compute_type = resolve_whisper_compute_type(
                        device, settings.whisper_compute_type
                    )
                    logger.info(
                        "Loading Whisper model '%s' (device=%s, compute=%s)",
                        settings.whisper_model,
                        device,
                        compute_type,
                    )
                    self._model = WhisperModel(
                        settings.whisper_model,
                        device=device,
                        compute_type=compute_type,
                    )
                    self._resolved_device = device
                    self._resolved_compute_type = compute_type
        return self._model

    def is_ready(self) -> bool:
        """Check that faster-whisper is available without loading the model."""
        try:
            from faster_whisper import WhisperModel  # noqa: F401

            return True
        except ImportError as exc:
            logger.warning("Whisper not ready: %s", exc)
            return False

    def transcribe(self, audio_path: Path) -> TranscriptResult:
        try:
            model = self._get_model()
            segments_iter, info = model.transcribe(str(audio_path), beam_size=5)

            segments: list[TranscriptSegment] = []
            text_parts: list[str] = []
            for segment in segments_iter:
                segments.append(
                    TranscriptSegment(
                        start=segment.start,
                        end=segment.end,
                        text=segment.text.strip(),
                    )
                )
                text_parts.append(segment.text.strip())

            return TranscriptResult(
                text=" ".join(text_parts).strip(),
                segments=segments,
                language=info.language,
                duration_seconds=info.duration,
            )
        except WhisperError:
            raise
        except Exception as exc:
            raise WhisperError(f"Transcription failed: {exc}") from exc


whisper_service = WhisperService()
