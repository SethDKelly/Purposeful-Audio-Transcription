from dataclasses import dataclass

from backend.services.diarization_service import SpeakerInterval
from backend.services.whisper_service import TranscriptSegment


@dataclass(frozen=True)
class LabeledTranscript:
    text: str
    speaker_labels: list[str]


def _overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def assign_speaker(
    segment: TranscriptSegment,
    timeline: list[SpeakerInterval],
) -> str | None:
    best_speaker: str | None = None
    best_overlap = 0.0
    midpoint = (segment.start + segment.end) / 2.0

    for interval in timeline:
        overlap = _overlap(segment.start, segment.end, interval.start, interval.end)
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = interval.speaker

    if best_speaker is not None:
        return best_speaker

    for interval in timeline:
        if interval.start <= midpoint <= interval.end:
            return interval.speaker

    return None


def _display_label(raw_speaker: str, speaker_order: dict[str, str], prefix: str) -> str:
    if raw_speaker not in speaker_order:
        index = len(speaker_order)
        if prefix == "Person":
            speaker_order[raw_speaker] = f"Person {chr(65 + index)}"
        else:
            speaker_order[raw_speaker] = f"{prefix} {index + 1}"
    return speaker_order[raw_speaker]


def build_labeled_transcript(
    segments: list[TranscriptSegment],
    timeline: list[SpeakerInterval],
    *,
    speaker_prefix: str = "Person",
    unknown_speaker_label: str = "Speaker 1",
) -> LabeledTranscript:
    if not segments:
        return LabeledTranscript(text="", speaker_labels=[])

    speaker_order: dict[str, str] = {}
    turns: list[tuple[str, str]] = []

    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue

        raw_speaker = assign_speaker(segment, timeline)
        if raw_speaker is None:
            display_label = unknown_speaker_label
        else:
            display_label = _display_label(raw_speaker, speaker_order, speaker_prefix)

        if turns and turns[-1][0] == display_label:
            turns[-1] = (display_label, f"{turns[-1][1]} {text}".strip())
        else:
            turns.append((display_label, text))

    if not turns:
        return LabeledTranscript(text="", speaker_labels=[])

    lines = [f"{label}: {text}" for label, text in turns]
    labels: list[str] = []
    for label, _text in turns:
        if label not in labels:
            labels.append(label)
    return LabeledTranscript(text="\n".join(lines), speaker_labels=labels)
