import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.core.exceptions import TranscriptNotFoundError, TranscriptValidationError
from backend.db.models import (
    ConstructEvidenceQuoteRow,
    ConstructRelationshipEvidenceQuoteRow,
    ConstructRelationshipRow,
    ConstructRow,
    ConstructSourceRow,
    EvidenceQuoteRow,
    FindingAlternativeExplanationRow,
    FindingEvidenceQuoteRow,
    FindingRow,
    ModuleRunRow,
    SpeakerRow,
    SynthesisReportRow,
    TranscriptRow,
    TurnRow,
    WorkflowRunRow,
)
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
                analysis_ready=transcript.analysis_ready,
                ready_at=transcript.ready_at,
                skip_review=transcript.skip_review,
                case_id=transcript.case_id,
                session_label=transcript.session_label,
                session_date=transcript.session_date,
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
                    excluded_from_analysis=turn.excluded_from_analysis,
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
            analysis_ready=bool(row.analysis_ready),
            ready_at=row.ready_at,
            skip_review=bool(row.skip_review),
            case_id=row.case_id,
            session_label=row.session_label,
            session_date=row.session_date,
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
                excluded_from_analysis=bool(turn.excluded_from_analysis),
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

    def update_turns(
        self,
        session: Session,
        transcript_id: str,
        patches: list[dict],
    ) -> None:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        speaker_ids = {speaker.id for speaker in row.speakers}
        turn_rows = {turn.id: turn for turn in row.turns}
        for patch in patches:
            turn_row = turn_rows.get(patch["id"])
            if turn_row is None:
                raise TranscriptNotFoundError(f"Turn not found: {patch['id']}")
            if "text" in patch and patch["text"] is not None:
                text = str(patch["text"]).strip()
                if not text:
                    raise TranscriptValidationError(
                        f"Turn text cannot be empty: {patch['id']}"
                    )
                turn_row.text = text
            if "speaker_id" in patch and patch["speaker_id"] is not None:
                speaker_id = str(patch["speaker_id"])
                if speaker_id not in speaker_ids:
                    raise TranscriptNotFoundError(f"Speaker not found: {speaker_id}")
                turn_row.speaker_id = speaker_id
            if "excluded_from_analysis" in patch and patch["excluded_from_analysis"] is not None:
                turn_row.excluded_from_analysis = bool(patch["excluded_from_analysis"])

        # Re-number turn_index in stable order
        ordered = sorted(row.turns, key=lambda t: t.turn_index)
        for index, turn_row in enumerate(ordered, start=1):
            turn_row.turn_index = index

        row.analysis_ready = False
        row.ready_at = None
        row.skip_review = False
        session.flush()

    def replace_evidence_quotes(
        self, session: Session, transcript_id: str, quotes: list[EvidenceQuote]
    ) -> None:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        session.execute(
            delete(EvidenceQuoteRow).where(EvidenceQuoteRow.transcript_id == transcript_id)
        )
        session.flush()
        for quote in quotes:
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
        session.flush()

    def sync_raw_text_from_turns(self, session: Session, transcript_id: str) -> None:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        speaker_names = {
            speaker.id: (speaker.display_name or speaker.label) for speaker in row.speakers
        }
        lines: list[str] = []
        for turn in sorted(row.turns, key=lambda t: t.turn_index):
            if turn.excluded_from_analysis:
                continue
            name = speaker_names.get(turn.speaker_id, "Unknown")
            lines.append(f"{name}: {turn.text}")
        row.raw_text = "\n".join(lines)
        session.flush()

    def set_preparation_state(
        self,
        session: Session,
        transcript_id: str,
        *,
        analysis_ready: bool,
        skip_review: bool = False,
        ready_at: datetime | None = None,
    ) -> None:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        row.analysis_ready = analysis_ready
        row.skip_review = skip_review
        row.ready_at = ready_at
        session.flush()

    def delete_cascade(self, session: Session, transcript_id: str) -> None:
        """Delete transcript and all dependent runs/reports/quotes/turns/speakers."""
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        run_ids = list(
            session.scalars(
                select(WorkflowRunRow.id).where(WorkflowRunRow.transcript_id == transcript_id)
            ).all()
        )
        module_run_ids = list(
            session.scalars(
                select(ModuleRunRow.id).where(ModuleRunRow.transcript_id == transcript_id)
            ).all()
        )
        if run_ids:
            workflow_module_ids = list(
                session.scalars(
                    select(ModuleRunRow.id).where(ModuleRunRow.workflow_run_id.in_(run_ids))
                ).all()
            )
            module_run_ids = list({*module_run_ids, *workflow_module_ids})

        if module_run_ids:
            finding_ids = list(
                session.scalars(
                    select(FindingRow.id).where(FindingRow.module_run_id.in_(module_run_ids))
                ).all()
            )
            if finding_ids:
                session.execute(
                    delete(FindingEvidenceQuoteRow).where(
                        FindingEvidenceQuoteRow.finding_id.in_(finding_ids)
                    )
                )
                session.execute(
                    delete(FindingAlternativeExplanationRow).where(
                        FindingAlternativeExplanationRow.finding_id.in_(finding_ids)
                    )
                )
                session.execute(delete(FindingRow).where(FindingRow.id.in_(finding_ids)))

            rel_ids = list(
                session.scalars(
                    select(ConstructRelationshipRow.id).where(
                        ConstructRelationshipRow.module_run_id.in_(module_run_ids)
                    )
                ).all()
            )
            if rel_ids:
                session.execute(
                    delete(ConstructRelationshipEvidenceQuoteRow).where(
                        ConstructRelationshipEvidenceQuoteRow.relationship_id.in_(rel_ids)
                    )
                )
                session.execute(
                    delete(ConstructRelationshipRow).where(
                        ConstructRelationshipRow.id.in_(rel_ids)
                    )
                )

            construct_ids = list(
                session.scalars(
                    select(ConstructRow.id).where(
                        ConstructRow.module_run_id.in_(module_run_ids)
                    )
                ).all()
            )
            if construct_ids:
                session.execute(
                    delete(ConstructEvidenceQuoteRow).where(
                        ConstructEvidenceQuoteRow.construct_id.in_(construct_ids)
                    )
                )
                session.execute(
                    delete(ConstructSourceRow).where(
                        ConstructSourceRow.construct_id.in_(construct_ids)
                    )
                )
                session.execute(
                    delete(ConstructRow).where(ConstructRow.id.in_(construct_ids))
                )

        if run_ids:
            session.execute(
                delete(SynthesisReportRow).where(
                    SynthesisReportRow.workflow_run_id.in_(run_ids)
                )
            )
            session.execute(
                delete(ModuleRunRow).where(ModuleRunRow.workflow_run_id.in_(run_ids))
            )
            session.execute(delete(WorkflowRunRow).where(WorkflowRunRow.id.in_(run_ids)))

        session.execute(
            delete(ModuleRunRow).where(ModuleRunRow.transcript_id == transcript_id)
        )
        session.execute(
            delete(EvidenceQuoteRow).where(EvidenceQuoteRow.transcript_id == transcript_id)
        )
        session.execute(delete(TurnRow).where(TurnRow.transcript_id == transcript_id))
        session.execute(delete(SpeakerRow).where(SpeakerRow.transcript_id == transcript_id))
        session.execute(delete(TranscriptRow).where(TranscriptRow.id == transcript_id))
        session.flush()

    def list_ids_created_before(
        self, session: Session, cutoff: datetime
    ) -> list[str]:
        rows = session.scalars(
            select(TranscriptRow.id).where(TranscriptRow.created_at < cutoff)
        ).all()
        return list(rows)


def new_transcript_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)
