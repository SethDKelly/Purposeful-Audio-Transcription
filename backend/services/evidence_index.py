import uuid

from backend.domain.transcript import EvidenceQuote, Speaker, TranscriptBundle
from backend.services.transcript_parser import ParsedTurn


class EvidenceIndexService:
    """Assign stable quote IDs and context to transcript turns."""

    def build_index(
        self,
        bundle: TranscriptBundle,
        parsed_turns: list[ParsedTurn],
        speaker_id_by_label: dict[str, str],
    ) -> list[EvidenceQuote]:
        quotes: list[EvidenceQuote] = []
        turn_texts = [turn.text for turn in parsed_turns]

        for index, (parsed_turn, turn) in enumerate(
            zip(parsed_turns, bundle.turns, strict=True), start=1
        ):
            quote_id = f"Q{index:03d}"
            context_before = turn_texts[index - 2] if index > 1 else None
            context_after = turn_texts[index] if index < len(turn_texts) else None

            quotes.append(
                EvidenceQuote(
                    id=str(uuid.uuid4()),
                    transcript_id=bundle.transcript.id,
                    turn_id=turn.id,
                    speaker_id=speaker_id_by_label[parsed_turn.speaker_label],
                    quote_index=index,
                    quote_id=quote_id,
                    text=parsed_turn.text,
                    context_before=_truncate(context_before),
                    context_after=_truncate(context_after),
                )
            )

        return quotes

    def lookup_by_quote_id(
        self, quotes: list[EvidenceQuote], quote_id: str
    ) -> EvidenceQuote | None:
        for quote in quotes:
            if quote.quote_id == quote_id:
                return quote
        return None

    def format_for_prompt(self, quotes: list[EvidenceQuote], speakers: list[Speaker]) -> str:
        speaker_names = {
            speaker.id: speaker.display_name or speaker.label for speaker in speakers
        }
        lines: list[str] = []
        for quote in quotes:
            name = speaker_names.get(quote.speaker_id, "Unknown")
            lines.append(f"[{quote.quote_id}] {name}: {quote.text}")
        return "\n".join(lines)


def _truncate(text: str | None, max_len: int = 200) -> str | None:
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
