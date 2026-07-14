"""Slice and filter audio for diarization-driven Whisper transcription."""

from dataclasses import dataclass

from backend.services.diarization_timeline import SpeakerInterval


@dataclass(frozen=True)
class SpeakerAudioSlice:
    speaker: str
    start: float
    end: float


def filter_intervals_for_transcription(
    intervals: list[SpeakerInterval],
    *,
    min_duration_seconds: float,
    max_slices: int,
) -> tuple[list[SpeakerAudioSlice], int]:
    """Keep intervals long enough for Whisper and cap slice count."""
    slices: list[SpeakerAudioSlice] = []
    skipped_short = 0

    for interval in sorted(intervals, key=lambda item: (item.start, item.end)):
        duration = interval.end - interval.start
        if duration < min_duration_seconds:
            skipped_short += 1
            continue
        slices.append(
            SpeakerAudioSlice(
                speaker=interval.speaker,
                start=interval.start,
                end=interval.end,
            )
        )

    if len(slices) > max_slices:
        omitted = len(slices) - max_slices
        slices = slices[:max_slices]
        return slices, skipped_short + omitted

    return slices, skipped_short


def speaker_for_timestamp(
    timestamp: float,
    slices: list[SpeakerAudioSlice],
) -> str | None:
    """Return the speaker active at a timestamp."""
    for slice_ in slices:
        if slice_.start <= timestamp <= slice_.end:
            return slice_.speaker

    best: SpeakerAudioSlice | None = None
    best_distance = float("inf")
    for slice_ in slices:
        if timestamp < slice_.start:
            distance = slice_.start - timestamp
        elif timestamp > slice_.end:
            distance = timestamp - slice_.end
        else:
            return slice_.speaker
        if distance < best_distance:
            best_distance = distance
            best = slice_

    return best.speaker if best is not None else None
