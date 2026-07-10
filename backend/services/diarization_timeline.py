"""Post-process pyannote speaker timelines to reduce label flipping."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeakerInterval:
    speaker: str
    start: float
    end: float


def merge_same_speaker_gaps(
    intervals: list[SpeakerInterval],
    max_gap_seconds: float,
) -> list[SpeakerInterval]:
    """Merge consecutive intervals for the same speaker when the gap is small."""
    if max_gap_seconds <= 0 or not intervals:
        return list(intervals)

    ordered = sorted(intervals, key=lambda item: (item.start, item.end))
    merged: list[SpeakerInterval] = []
    for interval in ordered:
        if (
            merged
            and merged[-1].speaker == interval.speaker
            and interval.start - merged[-1].end <= max_gap_seconds
        ):
            merged[-1] = SpeakerInterval(
                merged[-1].speaker,
                merged[-1].start,
                max(merged[-1].end, interval.end),
            )
        else:
            merged.append(interval)
    return merged


def absorb_short_intervals(
    intervals: list[SpeakerInterval],
    min_duration_seconds: float,
) -> list[SpeakerInterval]:
    """Remove or absorb intervals shorter than the minimum duration."""
    if min_duration_seconds <= 0 or not intervals:
        return list(intervals)

    current = list(intervals)
    while True:
        removed = False
        for index, interval in enumerate(current):
            duration = interval.end - interval.start
            if duration >= min_duration_seconds:
                continue

            previous = current[index - 1] if index > 0 else None
            nxt = current[index + 1] if index < len(current) - 1 else None

            if previous and nxt and previous.speaker == nxt.speaker:
                current[index - 1 : index + 2] = [
                    SpeakerInterval(previous.speaker, previous.start, nxt.end)
                ]
                removed = True
                break

            if previous and (
                nxt is None
                or (previous.end - previous.start) >= (nxt.end - nxt.start)
            ):
                current[index - 1] = SpeakerInterval(
                    previous.speaker,
                    previous.start,
                    max(previous.end, interval.end),
                )
                del current[index]
                removed = True
                break

            if nxt:
                current[index + 1] = SpeakerInterval(
                    nxt.speaker,
                    min(interval.start, nxt.start),
                    nxt.end,
                )
                del current[index]
                removed = True
                break

            del current[index]
            removed = True
            break

        if not removed:
            break
        current = merge_same_speaker_gaps(current, 0.0)

    return current


def smooth_speaker_timeline(
    intervals: list[SpeakerInterval],
    *,
    min_duration_on: float = 0.0,
    min_duration_off: float = 0.0,
) -> list[SpeakerInterval]:
    """Stabilize a diarization timeline by merging gaps and absorbing short turns."""
    if not intervals:
        return []

    smoothed = merge_same_speaker_gaps(
        sorted(intervals, key=lambda item: (item.start, item.end)),
        min_duration_off,
    )
    smoothed = absorb_short_intervals(smoothed, min_duration_on)
    return merge_same_speaker_gaps(smoothed, min_duration_off)
