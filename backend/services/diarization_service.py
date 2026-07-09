import logging
import os
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from backend.services.audio_service import (
    check_ffmpeg_available,
    check_ffprobe_available,
    load_waveform_for_diarization,
)
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpeakerInterval:
    speaker: str
    start: float
    end: float


def diarization_speaker_kwargs(num_speakers: int | None = None) -> dict[str, int]:
    """Build pyannote min/max speaker hints from a request or settings."""
    if num_speakers is not None:
        return {"min_speakers": num_speakers, "max_speakers": num_speakers}

    kwargs: dict[str, int] = {}
    if settings.diarization_min_speakers is not None:
        kwargs["min_speakers"] = settings.diarization_min_speakers
    if settings.diarization_max_speakers is not None:
        kwargs["max_speakers"] = settings.diarization_max_speakers
    return kwargs


class DiarizationService:
    def __init__(self) -> None:
        self._pipeline = None
        self._lock = Lock()

    def model_access_error(self) -> str | None:
        """Return a user-facing message when the HF model is not accessible."""
        if not settings.hf_token:
            return "HF_TOKEN is not set in .env"
        try:
            from huggingface_hub import hf_hub_download
            from huggingface_hub.errors import GatedRepoError

            hf_hub_download(
                settings.diarization_model,
                "config.yaml",
                token=settings.hf_token,
            )
            return None
        except GatedRepoError:
            return (
                f"Accept the model terms at "
                f"https://huggingface.co/{settings.diarization_model} "
                f"(and https://huggingface.co/pyannote/segmentation-3.0 if needed)"
            )
        except Exception as exc:
            return str(exc)

    def is_available(self) -> bool:
        """True when diarization is enabled and dependencies plus HF model access are present."""
        if not settings.diarization_enabled:
            return False
        if not settings.hf_token:
            return False
        if not check_ffmpeg_available() or not check_ffprobe_available():
            return False
        try:
            import pyannote.audio  # noqa: F401
        except ImportError:
            return False
        return self.model_access_error() is None

    def _get_pipeline(self):
        if self._pipeline is None:
            with self._lock:
                if self._pipeline is None:
                    from pyannote.audio import Pipeline

                    token = settings.hf_token
                    if token:
                        os.environ.setdefault("HF_TOKEN", token)
                    logger.info(
                        "Loading diarization pipeline '%s'",
                        settings.diarization_model,
                    )
                    self._pipeline = Pipeline.from_pretrained(
                        settings.diarization_model,
                        token=token or None,
                    )
        return self._pipeline

    def diarize(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None = None,
    ) -> list[SpeakerInterval]:
        if not self.is_available():
            raise RuntimeError("Diarization is not available")

        pipeline = self._get_pipeline()
        kwargs = diarization_speaker_kwargs(num_speakers)
        if kwargs:
            logger.info(
                "Diarizing %s with speaker hints: %s",
                audio_path.name,
                kwargs,
            )

        audio_input = load_waveform_for_diarization(audio_path)
        annotation = pipeline(audio_input, **kwargs)
        intervals: list[SpeakerInterval] = []
        for segment, _track, label in annotation.itertracks(yield_label=True):
            intervals.append(
                SpeakerInterval(
                    speaker=str(label),
                    start=float(segment.start),
                    end=float(segment.end),
                )
            )
        intervals.sort(key=lambda item: (item.start, item.end))
        logger.info(
            "Diarized %s: %s intervals, %s speakers",
            audio_path.name,
            len(intervals),
            len({item.speaker for item in intervals}),
        )
        return intervals


diarization_service = DiarizationService()
