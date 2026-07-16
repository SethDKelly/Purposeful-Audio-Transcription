import re
from dataclasses import dataclass

from backend.core.exceptions import TranscriptValidationError

SPEAKER_LINE_PATTERN = re.compile(r"^(?P<label>[^:\n]{1,80}):\s*(?P<text>.+)$")
DEFAULT_SPEAKER_LABEL = "Speaker 1"


@dataclass
class ParsedTurn:
    speaker_label: str
    text: str


class TranscriptParser:
    """Parse labeled transcript text into speaker turns."""

    def parse(self, raw_text: str) -> list[ParsedTurn]:
        text = raw_text.strip()
        if not text:
            raise TranscriptValidationError("Transcript text is empty")

        turns: list[ParsedTurn] = []
        current_label: str | None = None

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            match = SPEAKER_LINE_PATTERN.match(stripped)
            if match:
                current_label = match.group("label").strip()
                turn_text = match.group("text").strip()
                if turn_text:
                    turns.append(ParsedTurn(speaker_label=current_label, text=turn_text))
                else:
                    turns.append(ParsedTurn(speaker_label=current_label, text=""))
                continue

            if current_label is not None and turns:
                turns[-1].text = f"{turns[-1].text} {stripped}".strip()
            else:
                current_label = DEFAULT_SPEAKER_LABEL
                turns.append(ParsedTurn(speaker_label=current_label, text=stripped))

        if not turns:
            raise TranscriptValidationError("No turns could be parsed from transcript")

        return [turn for turn in turns if turn.text.strip()]
