import logging
from dataclasses import dataclass, field
from pathlib import Path

from backend.services.diarization_service import diarization_service
from backend.services.transcript_alignment_service import build_labeled_transcript
from backend.services.whisper_service import TranscriptResult, TranscriptSegment, whisper_service
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioTranscriptionResult:
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str | None = None
    duration_seconds: float | None = None
    speaker_count: int = 1
    speaker_labels: list[str] = field(default_factory=list)
    diarization_applied: bool = False


class AudioTranscriptionService:
    def transcribe(self, audio_path: Path) -> AudioTranscriptionResult:
        whisper_result = whisper_service.transcribe(audio_path)
        base = AudioTranscriptionResult(
            text=whisper_result.text,
            segments=whisper_result.segments,
            language=whisper_result.language,
            duration_seconds=whisper_result.duration_seconds,
            speaker_count=1,
            speaker_labels=["Speaker 1"],
            diarization_applied=False,
        )

        if not settings.diarization_enabled:
            return base

        if not diarization_service.is_available():
            logger.info(
                "Skipping diarization for %s (install pyannote extras and set HF_TOKEN)",
                audio_path.name,
            )
            return base

        try:
            timeline = diarization_service.diarize(audio_path)
            if not timeline:
                logger.warning("Diarization returned no intervals for %s", audio_path.name)
                return base

            labeled = build_labeled_transcript(
                whisper_result.segments,
                timeline,
                speaker_prefix=settings.diarization_speaker_prefix,
            )
            if not labeled.text.strip():
                return base

            speaker_count = len(labeled.speaker_labels) or 1
            return AudioTranscriptionResult(
                text=labeled.text,
                segments=whisper_result.segments,
                language=whisper_result.language,
                duration_seconds=whisper_result.duration_seconds,
                speaker_count=speaker_count,
                speaker_labels=labeled.speaker_labels,
                diarization_applied=True,
            )
        except Exception as exc:
            logger.warning(
                "Diarization failed for %s, using single-speaker transcript: %s",
                audio_path.name,
                exc,
            )
            return base


audio_transcription_service = AudioTranscriptionService()
