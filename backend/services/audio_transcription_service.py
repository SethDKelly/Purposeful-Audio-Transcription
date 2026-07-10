import logging
from dataclasses import dataclass, field
from pathlib import Path

from backend.services.diarization_service import diarization_service
from backend.services.transcript_alignment_service import (
    build_labeled_transcript,
    build_labeled_transcript_from_tagged,
)
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
    diarization_skip_reason: str | None = None
    transcription_mode: str = "overlap"


class AudioTranscriptionService:
    def transcribe(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None = None,
    ) -> AudioTranscriptionResult:
        mode = settings.transcription_mode.strip().lower()
        if mode == "sliced" and settings.diarization_enabled:
            sliced = self._try_transcribe_sliced(audio_path, num_speakers=num_speakers)
            if sliced is not None:
                return sliced
            logger.warning(
                "Sliced transcription unavailable for %s; falling back to overlap mode",
                audio_path.name,
            )
        return self._transcribe_overlap(audio_path, num_speakers=num_speakers)

    def _try_transcribe_sliced(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None,
    ) -> AudioTranscriptionResult | None:
        model_access_error = diarization_service.model_access_error()
        if model_access_error:
            return None
        if not diarization_service.is_available():
            return None

        try:
            timeline = diarization_service.diarize(audio_path, num_speakers=num_speakers)
            if not timeline:
                return None

            whisper_result = whisper_service.transcribe_speaker_intervals(
                audio_path,
                timeline,
            )
            if not whisper_result.tagged_segments:
                return None

            labeled = build_labeled_transcript_from_tagged(
                whisper_result.tagged_segments,
                speaker_prefix=settings.diarization_speaker_prefix,
            )
            if not labeled.text.strip():
                return None

            speaker_count = len(labeled.speaker_labels) or 1
            return AudioTranscriptionResult(
                text=labeled.text,
                segments=whisper_result.segments,
                language=whisper_result.language,
                duration_seconds=whisper_result.duration_seconds,
                speaker_count=speaker_count,
                speaker_labels=labeled.speaker_labels,
                diarization_applied=True,
                transcription_mode="sliced",
            )
        except Exception as exc:
            logger.warning(
                "Sliced transcription failed for %s: %s",
                audio_path.name,
                exc,
            )
            return None

    def _transcribe_overlap(
        self,
        audio_path: Path,
        *,
        num_speakers: int | None,
    ) -> AudioTranscriptionResult:
        whisper_result = whisper_service.transcribe(audio_path)
        base = AudioTranscriptionResult(
            text=whisper_result.text,
            segments=whisper_result.segments,
            language=whisper_result.language,
            duration_seconds=whisper_result.duration_seconds,
            speaker_count=1,
            speaker_labels=["Speaker 1"],
            diarization_applied=False,
            transcription_mode="overlap",
        )

        if not settings.diarization_enabled:
            base.diarization_skip_reason = "Diarization is disabled in settings"
            return base

        model_access_error = diarization_service.model_access_error()
        if model_access_error:
            logger.warning(
                "Skipping diarization for %s: %s",
                audio_path.name,
                model_access_error,
            )
            base.diarization_skip_reason = model_access_error
            return base

        if not diarization_service.is_available():
            reason = "Diarization dependencies are not available"
            logger.info("Skipping diarization for %s (%s)", audio_path.name, reason)
            base.diarization_skip_reason = reason
            return base

        try:
            timeline = diarization_service.diarize(audio_path, num_speakers=num_speakers)
            if not timeline:
                reason = "Diarization returned no speaker intervals"
                logger.warning("%s for %s", reason, audio_path.name)
                base.diarization_skip_reason = reason
                return base

            labeled = build_labeled_transcript(
                whisper_result.segments,
                timeline,
                speaker_prefix=settings.diarization_speaker_prefix,
            )
            if not labeled.text.strip():
                base.diarization_skip_reason = "Speaker alignment produced no labeled text"
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
                transcription_mode="overlap",
            )
        except Exception as exc:
            reason = str(exc)
            logger.warning(
                "Diarization failed for %s, using single-speaker transcript: %s",
                audio_path.name,
                exc,
            )
            base.diarization_skip_reason = reason
            return base


audio_transcription_service = AudioTranscriptionService()
