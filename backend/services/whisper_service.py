import logging
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from faster_whisper import WhisperModel

from config.settings import settings
from backend.core.exceptions import WhisperError

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

    def _resolve_device(self) -> str:
        if settings.whisper_device != "auto":
            return settings.whisper_device
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    device = self._resolve_device()
                    compute_type = settings.whisper_compute_type
                    if device == "cpu" and compute_type == "float16":
                        compute_type = "int8"
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
