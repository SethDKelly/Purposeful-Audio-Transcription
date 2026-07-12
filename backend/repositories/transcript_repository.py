import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.core.exceptions import TranscriptNotFoundError
from backend.db.models import EvidenceQuoteRow, SpeakerRow, TranscriptRow, TurnRow
from backend.domain.enums import SourceType
from backend.domain.transcript import (
    EvidenceQuote,
    Speaker,
    Transcript,
    TranscriptBundle,
    Turn,
)


class TranscriptRepository:
    def save_bundle(self, session: Session, bundle: TranscriptBundle) -> None:
        transcript = bundle.transcript
        session.add(
            TranscriptRow(
                id=transcript.id,
                title=transcript.title,
                raw_text=transcript.raw_text,
                source_type=transcript.source_type.value,
                language=transcript.language,
                created_at=transcript.created_at,
            )
        )
        for speaker in bundle.speakers:
            session.add(
                SpeakerRow(
                    id=speaker.id,
                    transcript_id=speaker.transcript_id,
                    label=speaker.label,
                    display_name=speaker.display_name,
                )
            )
        session.flush()
        for turn in bundle.turns:
            session.add(
                TurnRow(
                    id=turn.id,
                    transcript_id=turn.transcript_id,
                    speaker_id=turn.speaker_id,
                    turn_index=turn.turn_index,
                    text=turn.text,
                    start_time=turn.start_time,
                    end_time=turn.end_time,
                )
            )
        session.flush()
        for quote in bundle.evidence_quotes:
            session.add(
                EvidenceQuoteRow(
                    id=quote.id,
                    transcript_id=quote.transcript_id,
                    turn_id=quote.turn_id,
                    speaker_id=quote.speaker_id,
                    quote_index=quote.quote_index,
                    quote_id=quote.quote_id,
                    text=quote.text,
                    context_before=quote.context_before,
                    context_after=quote.context_after,
                )
            )

    def get_bundle(self, session: Session, transcript_id: str) -> TranscriptBundle:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        transcript = Transcript(
            id=row.id,
            title=row.title,
            raw_text=row.raw_text,
            source_type=SourceType(row.source_type),
            language=row.language,
            created_at=row.created_at,
        )
        speakers = [
            Speaker(
                id=speaker.id,
                transcript_id=speaker.transcript_id,
                label=speaker.label,
                display_name=speaker.display_name,
            )
            for speaker in sorted(row.speakers, key=lambda s: s.label)
        ]
        turns = [
            Turn(
                id=turn.id,
                transcript_id=turn.transcript_id,
                speaker_id=turn.speaker_id,
                turn_index=turn.turn_index,
                text=turn.text,
                start_time=turn.start_time,
                end_time=turn.end_time,
            )
            for turn in sorted(row.turns, key=lambda t: t.turn_index)
        ]
        quotes = [
            EvidenceQuote(
                id=quote.id,
                transcript_id=quote.transcript_id,
                turn_id=quote.turn_id,
                speaker_id=quote.speaker_id,
                quote_index=quote.quote_index,
                quote_id=quote.quote_id,
                text=quote.text,
                context_before=quote.context_before,
                context_after=quote.context_after,
            )
            for quote in sorted(row.evidence_quotes, key=lambda q: q.quote_index)
        ]
        return TranscriptBundle(
            transcript=transcript,
            speakers=speakers,
            turns=turns,
            evidence_quotes=quotes,
        )

    def update_speakers(
        self, session: Session, transcript_id: str, updates: list[Speaker]
    ) -> list[Speaker]:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        speaker_rows = {speaker.id: speaker for speaker in row.speakers}
        for update in updates:
            speaker_row = speaker_rows.get(update.id)
            if speaker_row is None:
                raise TranscriptNotFoundError(f"Speaker not found: {update.id}")
            if update.label:
                speaker_row.label = update.label
            if update.display_name is not None:
                speaker_row.display_name = update.display_name

        session.flush()
        return [
            Speaker(
                id=speaker.id,
                transcript_id=speaker.transcript_id,
                label=speaker.label,
                display_name=speaker.display_name,
            )
            for speaker in sorted(row.speakers, key=lambda s: s.label)
        ]


def new_transcript_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)
