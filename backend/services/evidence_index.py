import uuid

from backend.domain.transcript import EvidenceQuote, Speaker, TranscriptBundle
from backend.services.transcript_parser import ParsedTurn
from config.settings import settings

STRATEGY_FULL = "full"
STRATEGY_BALANCED_SAMPLE = "balanced_sample"
STRATEGY_HEAD_TAIL = "head_tail"


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
        strategy: str | None = None,
    ) -> tuple[list[EvidenceQuote], str | None, str]:
        """Return a subset when the evidence index exceeds prompt limits.

        Strategies: full | balanced_sample | head_tail. balanced_sample includes
        head, evenly spaced middle, and tail (never silent head/tail-only omission).
        """
        max_q = max_quotes if max_quotes is not None else settings.evidence_prompt_max_quotes
        if len(quotes) <= max_q:
            return quotes, None, STRATEGY_FULL

        use_strategy = strategy or STRATEGY_BALANCED_SAMPLE
        if use_strategy == STRATEGY_HEAD_TAIL:
            selected = self._select_head_tail(
                quotes,
                max_q=max_q,
                head_quotes=head_quotes,
                tail_quotes=tail_quotes,
            )
        else:
            selected = self._select_balanced_sample(
                quotes,
                max_q=max_q,
                head_quotes=head_quotes,
                tail_quotes=tail_quotes,
            )

        omitted = len(quotes) - len(selected)
        note = (
            f"[... {omitted} of {len(quotes)} evidence quotes omitted for prompt length "
            f"(strategy={use_strategy}); full index is retained in the database ...]"
        )
        return selected, note, use_strategy

    def _select_head_tail(
        self,
        quotes: list[EvidenceQuote],
        *,
        max_q: int,
        head_quotes: int | None,
        tail_quotes: int | None,
    ) -> list[EvidenceQuote]:
        head = head_quotes if head_quotes is not None else settings.evidence_prompt_head_quotes
        tail = tail_quotes if tail_quotes is not None else settings.evidence_prompt_tail_quotes
        head = min(head, len(quotes))
        tail = min(tail, max(0, len(quotes) - head))
        if head + tail >= len(quotes):
            return list(quotes)
        return quotes[:head] + quotes[len(quotes) - tail :]

    def _select_balanced_sample(
        self,
        quotes: list[EvidenceQuote],
        *,
        max_q: int,
        head_quotes: int | None,
        tail_quotes: int | None,
    ) -> list[EvidenceQuote]:
        total = len(quotes)
        head_budget = head_quotes if head_quotes is not None else settings.evidence_prompt_head_quotes
        tail_budget = tail_quotes if tail_quotes is not None else settings.evidence_prompt_tail_quotes
        # Reserve middle slots so sampling is not head/tail-only.
        head_n = min(head_budget, max(1, max_q // 4), total)
        tail_n = min(tail_budget, max(1, max_q // 4), max(0, total - head_n))
        middle_n = max(0, max_q - head_n - tail_n)
        middle_start = head_n
        middle_end = total - tail_n
        middle_available = max(0, middle_end - middle_start)

        selected_indices: list[int] = list(range(head_n))
        if middle_n > 0 and middle_available > 0:
            if middle_available <= middle_n:
                selected_indices.extend(range(middle_start, middle_end))
            else:
                step = middle_available / middle_n
                for slot in range(middle_n):
                    idx = middle_start + int(slot * step)
                    if idx < middle_end and idx not in selected_indices:
                        selected_indices.append(idx)
        if tail_n > 0:
            selected_indices.extend(range(total - tail_n, total))

        seen: set[int] = set()
        ordered: list[int] = []
        for idx in selected_indices:
            if idx not in seen:
                seen.add(idx)
                ordered.append(idx)
        ordered.sort()
        if len(ordered) > max_q:
            ordered = ordered[:max_q]
        return [quotes[i] for i in ordered]

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
        selected, omission_note, _strategy = self.select_quotes_for_prompt(
            quotes,
            max_quotes=max_quotes,
            head_quotes=head_quotes,
            tail_quotes=tail_quotes,
        )
        lines: list[str] = []
        omission_insert_at: int | None = None
        if omission_note and len(selected) > 1:
            for index in range(1, len(selected)):
                if selected[index].quote_index != selected[index - 1].quote_index + 1:
                    omission_insert_at = index
                    break

        for index, quote in enumerate(selected):
            if omission_note and index == omission_insert_at:
                lines.append(omission_note)
            name = speaker_names.get(quote.speaker_id, "Unknown")
            lines.append(f"[{quote.quote_id}] {name}: {quote.text}")
        if omission_note and omission_insert_at is None and len(selected) > 0:
            # head_tail strategy: note after head block
            head_count = min(
                head_quotes if head_quotes is not None else settings.evidence_prompt_head_quotes,
                len(quotes),
            )
            if head_count < len(selected):
                lines.insert(head_count, omission_note)
            else:
                lines.append(omission_note)
        return "\n".join(lines)


def _truncate(text: str | None, max_len: int = 200) -> str | None:
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
