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
    TranscriptVersionRow,
    TurnRow,
    WorkflowRunRow,
)
from backend.domain.enums import SourceType, WorkflowRunStatus
from backend.domain.transcript import (
    EvidenceQuote,
    Speaker,
    Transcript,
    TranscriptBundle,
    TranscriptVersion,
    Turn,
)


class TranscriptRepository:
    def save_bundle(
        self,
        session: Session,
        bundle: TranscriptBundle,
        *,
        owner_user_id: str | None = None,
    ) -> None:
        transcript = bundle.transcript
        version_id = transcript.current_version_id or (
            bundle.transcript_version.id if bundle.transcript_version else None
        )
        if version_id is None:
            version_id = new_transcript_id()
            transcript.current_version_id = version_id

        version = bundle.transcript_version
        if version is None:
            version = TranscriptVersion(
                id=version_id,
                transcript_id=transcript.id,
                version_number=1,
                created_at=transcript.created_at,
                source_type=(
                    transcript.source_type.value
                    if hasattr(transcript.source_type, "value")
                    else str(transcript.source_type)
                ),
                change_summary="Initial version",
                is_current=True,
            )
            bundle.transcript_version = version

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
                owner_user_id=owner_user_id,
                current_version_id=version_id,
            )
        )
        session.flush()
        session.add(
            TranscriptVersionRow(
                id=version.id,
                transcript_id=version.transcript_id,
                version_number=version.version_number,
                created_at=version.created_at,
                created_by_user_id=version.created_by_user_id,
                source_type=version.source_type,
                change_summary=version.change_summary,
                is_current=True,
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
            quote_version_id = quote.transcript_version_id or version_id
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
                    evidence_type=quote.evidence_type,
                    span_text=quote.span_text,
                    transcript_version_id=quote_version_id,
                )
            )

    def get_bundle(
        self,
        session: Session,
        transcript_id: str,
        version_id: str | None = None,
    ) -> TranscriptBundle:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        resolved_version_id = version_id or row.current_version_id
        version_row = None
        if resolved_version_id:
            version_row = session.get(TranscriptVersionRow, resolved_version_id)
        elif row.current_version_id:
            version_row = session.get(TranscriptVersionRow, row.current_version_id)

        current_version_number = None
        if row.current_version_id:
            current_row = (
                version_row
                if version_row and version_row.id == row.current_version_id
                else session.get(TranscriptVersionRow, row.current_version_id)
            )
            if current_row is not None:
                current_version_number = current_row.version_number

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
            current_version_id=row.current_version_id,
            current_version_number=current_version_number,
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

        quote_rows = list(row.evidence_quotes)
        if resolved_version_id is not None:
            quote_rows = [
                q for q in quote_rows if q.transcript_version_id == resolved_version_id
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
                evidence_type=getattr(quote, "evidence_type", None) or "atomic_quote",
                span_text=getattr(quote, "span_text", None),
                transcript_version_id=getattr(quote, "transcript_version_id", None),
            )
            for quote in sorted(quote_rows, key=lambda q: q.quote_index)
        ]

        transcript_version = _version_from_row(version_row) if version_row else None
        return TranscriptBundle(
            transcript=transcript,
            speakers=speakers,
            turns=turns,
            evidence_quotes=quotes,
            transcript_version=transcript_version,
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
        self,
        session: Session,
        transcript_id: str,
        quotes: list[EvidenceQuote],
        *,
        version_id: str,
    ) -> None:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        session.execute(
            delete(EvidenceQuoteRow).where(
                EvidenceQuoteRow.transcript_id == transcript_id,
                EvidenceQuoteRow.transcript_version_id == version_id,
            )
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
                    evidence_type=quote.evidence_type,
                    span_text=quote.span_text,
                    transcript_version_id=quote.transcript_version_id or version_id,
                )
            )
        session.flush()

    def create_new_version(
        self,
        session: Session,
        transcript_id: str,
        *,
        change_summary: str,
        source_type: str | None = None,
    ) -> TranscriptVersion:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

        existing = list(
            session.scalars(
                select(TranscriptVersionRow).where(
                    TranscriptVersionRow.transcript_id == transcript_id
                )
            ).all()
        )
        next_number = max((v.version_number for v in existing), default=0) + 1
        for version in existing:
            version.is_current = False

        version_id = new_transcript_id()
        now = utc_now().replace(tzinfo=None)
        version_row = TranscriptVersionRow(
            id=version_id,
            transcript_id=transcript_id,
            version_number=next_number,
            created_at=now,
            created_by_user_id=None,
            source_type=source_type or row.source_type,
            change_summary=change_summary,
            is_current=True,
        )
        session.add(version_row)
        row.current_version_id = version_id
        session.flush()
        return _version_from_row(version_row)

    def has_completed_workflow_runs(self, session: Session, transcript_id: str) -> bool:
        row = session.scalars(
            select(WorkflowRunRow.id)
            .where(WorkflowRunRow.transcript_id == transcript_id)
            .where(WorkflowRunRow.status == WorkflowRunStatus.COMPLETED.value)
            .limit(1)
        ).first()
        return row is not None

    def get_version(self, session: Session, version_id: str) -> TranscriptVersion:
        row = session.get(TranscriptVersionRow, version_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript version not found: {version_id}")
        return _version_from_row(row)

    def list_versions(self, session: Session, transcript_id: str) -> list[TranscriptVersion]:
        row = session.get(TranscriptRow, transcript_id)
        if row is None:
            raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")
        versions = list(
            session.scalars(
                select(TranscriptVersionRow)
                .where(TranscriptVersionRow.transcript_id == transcript_id)
                .order_by(TranscriptVersionRow.version_number.asc())
            ).all()
        )
        return [_version_from_row(v) for v in versions]

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
        # Clear version pointer before deleting version rows (FK-safe).
        row.current_version_id = None
        session.flush()
        session.execute(
            delete(EvidenceQuoteRow).where(EvidenceQuoteRow.transcript_id == transcript_id)
        )
        session.execute(
            delete(TranscriptVersionRow).where(
                TranscriptVersionRow.transcript_id == transcript_id
            )
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


def _version_from_row(row: TranscriptVersionRow) -> TranscriptVersion:
    return TranscriptVersion(
        id=row.id,
        transcript_id=row.transcript_id,
        version_number=row.version_number,
        created_at=row.created_at,
        created_by_user_id=row.created_by_user_id,
        source_type=row.source_type,
        change_summary=row.change_summary,
        is_current=bool(row.is_current),
    )
