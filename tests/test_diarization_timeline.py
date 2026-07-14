from backend.services.diarization_timeline import (
    SpeakerInterval,
    absorb_short_intervals,
    merge_same_speaker_gaps,
    smooth_speaker_timeline,
)


def _interval(speaker: str, start: float, end: float) -> SpeakerInterval:
    return SpeakerInterval(speaker=speaker, start=start, end=end)


def test_merge_same_speaker_gaps_merges_small_gap() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("A", 2.15, 4.0),
    ]

    merged = merge_same_speaker_gaps(intervals, max_gap_seconds=0.2)

    assert merged == [_interval("A", 0.0, 4.0)]


def test_merge_same_speaker_gaps_keeps_large_gap() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("A", 2.5, 4.0),
    ]

    merged = merge_same_speaker_gaps(intervals, max_gap_seconds=0.2)

    assert merged == intervals


def test_absorb_short_intervals_removes_speaker_flip() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("B", 2.0, 2.1),
        _interval("A", 2.1, 4.0),
    ]

    smoothed = absorb_short_intervals(intervals, min_duration_seconds=0.3)

    assert smoothed == [_interval("A", 0.0, 4.0)]


def test_absorb_short_intervals_extends_into_longer_neighbor() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("B", 2.0, 2.1),
        _interval("C", 2.1, 5.0),
    ]

    smoothed = absorb_short_intervals(intervals, min_duration_seconds=0.3)

    assert smoothed == [
        _interval("A", 0.0, 2.0),
        _interval("C", 2.0, 5.0),
    ]


def test_smooth_speaker_timeline_applies_gap_merge_and_short_turn_filter() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("B", 2.05, 2.15),
        _interval("A", 2.18, 4.0),
    ]

    smoothed = smooth_speaker_timeline(
        intervals,
        min_duration_on=0.3,
        min_duration_off=0.2,
    )

    assert smoothed == [_interval("A", 0.0, 4.0)]
