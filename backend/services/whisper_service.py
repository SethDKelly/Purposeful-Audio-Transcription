import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any

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

    def _transcribe_kwargs(self) -> dict[str, Any]:
        return {
            "beam_size": settings.whisper_beam_size,
            "vad_filter": settings.whisper_vad_filter,
            "condition_on_previous_text": False,
        }

    def iter_transcription_events(self, audio_path: Path) -> Iterator[dict[str, Any]]:
        """Yield NDJSON-friendly progress events, then a complete event with the result."""
        started = time.monotonic()
        try:
            model = self._get_model()
            segments_iter, info = model.transcribe(
                str(audio_path),
                **self._transcribe_kwargs(),
            )
            duration = info.duration if info.duration and info.duration > 0 else None
            yield {
                "type": "started",
                "elapsed_seconds": 0.0,
                "duration_seconds": duration,
                "language": info.language,
            }

            segments: list[TranscriptSegment] = []
            text_parts: list[str] = []
            for index, segment in enumerate(segments_iter, start=1):
                transcript_segment = TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                )
                segments.append(transcript_segment)
                text_parts.append(transcript_segment.text)
                elapsed = time.monotonic() - started
                progress_ratio = (
                    min(transcript_segment.end / duration, 1.0)
                    if duration
                    else None
                )
                yield {
                    "type": "progress",
                    "elapsed_seconds": round(elapsed, 1),
                    "segment_index": index,
                    "audio_position_seconds": round(transcript_segment.end, 1),
                    "duration_seconds": duration,
                    "progress_ratio": progress_ratio,
                    "partial_text": transcript_segment.text,
                }

            result = TranscriptResult(
                text=" ".join(text_parts).strip(),
                segments=segments,
                language=info.language,
                duration_seconds=duration,
            )
            elapsed = time.monotonic() - started
            logger.info(
                "Transcribed %s in %.1fs (%s segments)",
                audio_path.name,
                elapsed,
                len(segments),
            )
            yield {
                "type": "complete",
                "elapsed_seconds": round(elapsed, 1),
                "result": _result_to_dict(result),
            }
        except Exception as exc:
            elapsed = time.monotonic() - started
            logger.exception("Transcription failed after %.1fs", elapsed)
            yield {
                "type": "error",
                "elapsed_seconds": round(elapsed, 1),
                "message": str(exc),
            }
            return

    def transcribe(self, audio_path: Path) -> TranscriptResult:
        result: TranscriptResult | None = None
        for event in self.iter_transcription_events(audio_path):
            if event["type"] == "error":
                raise WhisperError(event.get("message", "Transcription failed"))
            if event["type"] == "complete":
                result = _result_from_dict(event["result"])
        if result is None:
            raise WhisperError("Transcription finished without a result")
        return result


def _result_to_dict(result: TranscriptResult) -> dict[str, Any]:
    return {
        "transcript": result.text,
        "segments": [
            {"start": seg.start, "end": seg.end, "text": seg.text}
            for seg in result.segments
        ],
        "language": result.language,
        "duration_seconds": result.duration_seconds,
    }


def _result_from_dict(payload: dict[str, Any]) -> TranscriptResult:
    return TranscriptResult(
        text=payload["transcript"],
        segments=[
            TranscriptSegment(
                start=segment["start"],
                end=segment["end"],
                text=segment["text"],
            )
            for segment in payload["segments"]
        ],
        language=payload.get("language"),
        duration_seconds=payload.get("duration_seconds"),
    )


whisper_service = WhisperService()
