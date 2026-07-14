import logging
from pathlib import Path
from threading import Lock
from typing import Any

from backend.core.device import resolve_whisper_compute_type, resolve_whisper_device
from backend.core.exceptions import WhisperError
from backend.services.audio_slicing import (
    SpeakerAudioSlice,
    filter_intervals_for_transcription,
    speaker_for_timestamp,
)
from backend.services.diarization_timeline import SpeakerInterval
from backend.services.transcript_types import (
    TaggedSegment,
    TranscriptResult,
    TranscriptSegment,
)
from config.settings import settings

logger = logging.getLogger(__name__)


class WhisperService:
    def __init__(self) -> None:
        self._model: Any | None = None
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

    def _get_model(self) -> Any:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from faster_whisper import WhisperModel

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

    def transcribe_speaker_intervals(
        self,
        audio_path: Path,
        intervals: list[SpeakerInterval],
    ) -> TranscriptResult:
        """Transcribe each diarization interval; segments inherit the slice speaker."""
        min_duration = max(
            settings.diarization_min_duration_on,
            settings.whisper_min_slice_duration,
        )
        slices, skipped = filter_intervals_for_transcription(
            intervals,
            min_duration_seconds=min_duration,
            max_slices=settings.whisper_max_slices,
        )
        if skipped:
            logger.info(
                "Skipped %s diarization intervals shorter than %.2fs for Whisper",
                skipped,
                min_duration,
            )
        if not slices:
            raise WhisperError("No speaker intervals long enough to transcribe")

        try:
            model = self._get_model()
            if self.resolved_device() == "cuda":
                return self._transcribe_slices_batched(model, audio_path, slices)
            return self._transcribe_slices_sequential(model, audio_path, slices)
        except WhisperError:
            raise
        except Exception as exc:
            raise WhisperError(f"Sliced transcription failed: {exc}") from exc

    def _transcribe_slices_sequential(
        self,
        model: Any,
        audio_path: Path,
        slices: list[SpeakerAudioSlice],
    ) -> TranscriptResult:
        from faster_whisper.audio import decode_audio

        audio = decode_audio(str(audio_path))
        sample_rate = 16_000
        segments: list[TranscriptSegment] = []
        tagged_segments: list[TaggedSegment] = []
        text_parts: list[str] = []
        language: str | None = None
        duration_seconds = len(audio) / sample_rate

        for slice_ in slices:
            start_index = int(slice_.start * sample_rate)
            end_index = int(slice_.end * sample_rate)
            clip = audio[start_index:end_index]
            if clip.size == 0:
                continue

            segments_iter, info = model.transcribe(
                clip,
                beam_size=5,
                condition_on_previous_text=False,
            )
            if language is None:
                language = info.language

            for segment in segments_iter:
                text = segment.text.strip()
                if not text:
                    continue
                transcript_segment = TranscriptSegment(
                    start=slice_.start + segment.start,
                    end=slice_.start + segment.end,
                    text=text,
                )
                segments.append(transcript_segment)
                tagged_segments.append(
                    TaggedSegment(segment=transcript_segment, speaker=slice_.speaker)
                )
                text_parts.append(text)

        return TranscriptResult(
            text=" ".join(text_parts).strip(),
            segments=segments,
            language=language,
            duration_seconds=duration_seconds,
            tagged_segments=tagged_segments,
        )

    def _transcribe_slices_batched(
        self,
        model: Any,
        audio_path: Path,
        slices: list[SpeakerAudioSlice],
    ) -> TranscriptResult:
        from faster_whisper import BatchedInferencePipeline

        pipeline = BatchedInferencePipeline(model)
        clip_timestamps = [{"start": slice_.start, "end": slice_.end} for slice_ in slices]
        segments_iter, info = pipeline.transcribe(
            str(audio_path),
            clip_timestamps=clip_timestamps,
            vad_filter=False,
            batch_size=settings.whisper_batch_size,
            beam_size=5,
            condition_on_previous_text=False,
        )

        segments: list[TranscriptSegment] = []
        tagged_segments: list[TaggedSegment] = []
        text_parts: list[str] = []

        for segment in segments_iter:
            text = segment.text.strip()
            if not text:
                continue
            midpoint = (segment.start + segment.end) / 2.0
            speaker = speaker_for_timestamp(midpoint, slices)
            if speaker is None:
                continue
            transcript_segment = TranscriptSegment(
                start=segment.start,
                end=segment.end,
                text=text,
            )
            segments.append(transcript_segment)
            tagged_segments.append(
                TaggedSegment(segment=transcript_segment, speaker=speaker)
            )
            text_parts.append(text)

        return TranscriptResult(
            text=" ".join(text_parts).strip(),
            segments=segments,
            language=info.language,
            duration_seconds=info.duration,
            tagged_segments=tagged_segments,
        )


whisper_service = WhisperService()
