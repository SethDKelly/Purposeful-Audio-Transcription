from backend.services.audio_slicing import (
    SpeakerAudioSlice,
    filter_intervals_for_transcription,
    speaker_for_timestamp,
)
from backend.services.diarization_timeline import SpeakerInterval


def _interval(speaker: str, start: float, end: float) -> SpeakerInterval:
    return SpeakerInterval(speaker=speaker, start=start, end=end)


def test_filter_intervals_for_transcription_drops_short_slices() -> None:
    intervals = [
        _interval("A", 0.0, 2.0),
        _interval("B", 2.0, 2.3),
        _interval("A", 2.3, 5.0),
    ]

    slices, skipped = filter_intervals_for_transcription(
        intervals,
        min_duration_seconds=0.5,
        max_slices=10,
    )

    assert skipped == 1
    assert len(slices) == 2
    assert slices[0].speaker == "A"
    assert slices[1].speaker == "A"


def test_filter_intervals_for_transcription_caps_slice_count() -> None:
    intervals = [_interval("A", index, index + 1.0) for index in range(5)]

    slices, skipped = filter_intervals_for_transcription(
        intervals,
        min_duration_seconds=0.5,
        max_slices=3,
    )

    assert len(slices) == 3
    assert skipped == 2


def test_speaker_for_timestamp_returns_active_speaker() -> None:
    slices = [
        SpeakerAudioSlice(speaker="A", start=0.0, end=2.0),
        SpeakerAudioSlice(speaker="B", start=2.0, end=4.0),
    ]

    assert speaker_for_timestamp(1.0, slices) == "A"
    assert speaker_for_timestamp(3.0, slices) == "B"
