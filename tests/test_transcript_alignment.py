from backend.services.diarization_service import SpeakerInterval
from backend.services.transcript_alignment_service import (
    assign_speaker,
    build_labeled_transcript,
    build_labeled_transcript_from_tagged,
)
from backend.services.transcript_types import TaggedSegment, TranscriptSegment


def test_assign_speaker_uses_max_overlap() -> None:
    segment = TranscriptSegment(start=2.5, end=3.5, text="hello")
    timeline = [
        SpeakerInterval(speaker="SPEAKER_00", start=0.0, end=2.0),
        SpeakerInterval(speaker="SPEAKER_01", start=2.0, end=5.0),
    ]
    assert assign_speaker(segment, timeline) == "SPEAKER_01"


def test_build_labeled_transcript_two_speakers() -> None:
    segments = [
        TranscriptSegment(start=0.0, end=2.0, text="Hello there."),
        TranscriptSegment(start=2.0, end=4.0, text="Hi back."),
        TranscriptSegment(start=4.0, end=6.0, text="How are you?"),
    ]
    timeline = [
        SpeakerInterval(speaker="SPEAKER_00", start=0.0, end=2.5),
        SpeakerInterval(speaker="SPEAKER_01", start=2.5, end=4.5),
        SpeakerInterval(speaker="SPEAKER_00", start=4.5, end=6.5),
    ]

    labeled = build_labeled_transcript(segments, timeline)

    assert labeled.speaker_labels == ["Person A", "Person B"]
    assert labeled.text == (
        "Person A: Hello there.\n"
        "Person B: Hi back.\n"
        "Person A: How are you?"
    )


def test_build_labeled_transcript_merges_consecutive_same_speaker() -> None:
    segments = [
        TranscriptSegment(start=0.0, end=1.0, text="One."),
        TranscriptSegment(start=1.0, end=2.0, text="Two."),
    ]
    timeline = [SpeakerInterval(speaker="SPEAKER_00", start=0.0, end=2.0)]

    labeled = build_labeled_transcript(segments, timeline)

    assert labeled.text == "Person A: One. Two."
    assert labeled.speaker_labels == ["Person A"]


def test_build_labeled_transcript_from_tagged_segments() -> None:
    tagged = [
        TaggedSegment(
            segment=TranscriptSegment(start=0.0, end=2.0, text="Hello there."),
            speaker="SPEAKER_00",
        ),
        TaggedSegment(
            segment=TranscriptSegment(start=2.0, end=4.0, text="Hi back."),
            speaker="SPEAKER_01",
        ),
    ]

    labeled = build_labeled_transcript_from_tagged(tagged)

    assert labeled.speaker_labels == ["Person A", "Person B"]
    assert labeled.text == "Person A: Hello there.\nPerson B: Hi back."
