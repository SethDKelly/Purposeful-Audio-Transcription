import logging
import os
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpeakerInterval:
    speaker: str
    start: float
    end: float


class DiarizationService:
    def __init__(self) -> None:
        self._pipeline = None
        self._lock = Lock()

    def is_available(self) -> bool:
        """True when diarization is enabled and dependencies plus HF token are present."""
        if not settings.diarization_enabled:
            return False
        if not settings.hf_token:
            return False
        try:
            import pyannote.audio  # noqa: F401

            return True
        except ImportError:
            return False

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

    def diarize(self, audio_path: Path) -> list[SpeakerInterval]:
        if not self.is_available():
            raise RuntimeError("Diarization is not available")

        pipeline = self._get_pipeline()
        kwargs: dict = {}
        if settings.diarization_min_speakers is not None:
            kwargs["min_speakers"] = settings.diarization_min_speakers
        if settings.diarization_max_speakers is not None:
            kwargs["max_speakers"] = settings.diarization_max_speakers

        annotation = pipeline(str(audio_path), **kwargs)
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
