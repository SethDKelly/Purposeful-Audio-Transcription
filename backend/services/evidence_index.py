import uuid

from backend.domain.transcript import EvidenceQuote, Speaker, TranscriptBundle
from backend.services.transcript_parser import ParsedTurn
from config.settings import settings


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

    def build_index_from_turns(
        self,
        transcript_id: str,
        turns: list,
        *,
        include_excluded: bool = False,
    ) -> list[EvidenceQuote]:
        """Rebuild quote IDs from current turn rows (skips excluded by default)."""
        from backend.domain.transcript import Turn

        ordered = sorted(turns, key=lambda t: t.turn_index)
        included: list[Turn] = [
            turn
            for turn in ordered
            if include_excluded or not getattr(turn, "excluded_from_analysis", False)
        ]
        turn_texts = [turn.text for turn in included]
        quotes: list[EvidenceQuote] = []
        for index, turn in enumerate(included, start=1):
            quotes.append(
                EvidenceQuote(
                    id=str(uuid.uuid4()),
                    transcript_id=transcript_id,
                    turn_id=turn.id,
                    speaker_id=turn.speaker_id,
                    quote_index=index,
                    quote_id=f"Q{index:03d}",
                    text=turn.text,
                    context_before=_truncate(turn_texts[index - 2] if index > 1 else None),
                    context_after=_truncate(
                        turn_texts[index] if index < len(turn_texts) else None
                    ),
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

    def select_quotes_for_prompt(
        self,
        quotes: list[EvidenceQuote],
        *,
        max_quotes: int | None = None,
        head_quotes: int | None = None,
        tail_quotes: int | None = None,
    ) -> tuple[list[EvidenceQuote], str | None]:
        """Return a head/tail subset when the evidence index exceeds prompt limits."""
        max_q = max_quotes if max_quotes is not None else settings.evidence_prompt_max_quotes
        if len(quotes) <= max_q:
            return quotes, None

        head = head_quotes if head_quotes is not None else settings.evidence_prompt_head_quotes
        tail = tail_quotes if tail_quotes is not None else settings.evidence_prompt_tail_quotes
        head = min(head, len(quotes))
        tail = min(tail, max(0, len(quotes) - head))

        if head + tail >= len(quotes):
            return quotes, None

        selected = quotes[:head] + quotes[len(quotes) - tail :]
        omitted = len(quotes) - len(selected)
        note = (
            f"[... {omitted} of {len(quotes)} evidence quotes omitted for prompt length; "
            "full index is retained in the database ...]"
        )
        return selected, note

    def format_for_prompt(
        self,
        quotes: list[EvidenceQuote],
        speakers: list[Speaker],
        *,
        max_quotes: int | None = None,
        head_quotes: int | None = None,
        tail_quotes: int | None = None,
    ) -> str:
        speaker_names = {
            speaker.id: speaker.display_name or speaker.label for speaker in speakers
        }
        selected, omission_note = self.select_quotes_for_prompt(
            quotes,
            max_quotes=max_quotes,
            head_quotes=head_quotes,
            tail_quotes=tail_quotes,
        )
        lines: list[str] = []
        head_count = 0
        if omission_note:
            head_count = min(
                head_quotes if head_quotes is not None else settings.evidence_prompt_head_quotes,
                len(quotes),
            )

        for index, quote in enumerate(selected):
            if omission_note and index == head_count:
                lines.append(omission_note)
            name = speaker_names.get(quote.speaker_id, "Unknown")
            lines.append(f"[{quote.quote_id}] {name}: {quote.text}")
        return "\n".join(lines)


def _truncate(text: str | None, max_len: int = 200) -> str | None:
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
