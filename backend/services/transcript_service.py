import uuid
from datetime import UTC, datetime, timedelta

from backend.core.audit import audit_event
from backend.core.exceptions import (
    TranscriptNotFoundError,
    TranscriptNotReadyError,
    TranscriptValidationError,
)
from backend.db.base import get_session
from backend.domain.enums import SourceType
from backend.domain.transcript import Speaker, Transcript, TranscriptBundle, Turn
from backend.repositories.transcript_repository import (
    TranscriptRepository,
    new_transcript_id,
    utc_now,
)
from backend.services.evidence_index import EvidenceIndexService
from backend.services.transcript_parser import TranscriptParser
from config.settings import settings


class TranscriptService:
    def __init__(self) -> None:
        self._parser = TranscriptParser()
        self._evidence_index = EvidenceIndexService()
        self._repository = TranscriptRepository()

    def ingest(
        self,
        raw_text: str,
        source_type: SourceType,
        title: str | None = None,
        language: str | None = None,
    ) -> TranscriptBundle:
        parsed_turns = self._parser.parse(raw_text)
        transcript_id = new_transcript_id()
        now = utc_now()

        transcript = Transcript(
            id=transcript_id,
            title=title or _default_title(source_type),
            raw_text=raw_text.strip(),
            source_type=source_type,
            language=language,
            created_at=now,
            analysis_ready=False,
            ready_at=None,
            skip_review=False,
        )

        speaker_id_by_label: dict[str, str] = {}
        speakers: list[Speaker] = []
        for label in _unique_labels(parsed_turns):
            speaker_id = str(uuid.uuid4())
            speaker_id_by_label[label] = speaker_id
            speakers.append(
                Speaker(
                    id=speaker_id,
                    transcript_id=transcript_id,
                    label=label,
                    display_name=label,
                )
            )

        turns: list[Turn] = []
        for index, parsed_turn in enumerate(parsed_turns, start=1):
            turns.append(
                Turn(
                    id=str(uuid.uuid4()),
                    transcript_id=transcript_id,
                    speaker_id=speaker_id_by_label[parsed_turn.speaker_label],
                    turn_index=index,
                    text=parsed_turn.text,
                    excluded_from_analysis=False,
                )
            )

        bundle = TranscriptBundle(
            transcript=transcript,
            speakers=speakers,
            turns=turns,
            evidence_quotes=[],
        )
        bundle.evidence_quotes = self._evidence_index.build_index(
            bundle, parsed_turns, speaker_id_by_label
        )

        with get_session() as session:
            self._repository.save_bundle(session, bundle)

        audit_event(
            "transcript.ingest",
            transcript_id=transcript_id,
            source_type=source_type.value,
            turn_count=len(turns),
            quote_count=len(bundle.evidence_quotes),
        )
        return bundle

    def get(self, transcript_id: str) -> TranscriptBundle:
        with get_session() as session:
            return self._repository.get_bundle(session, transcript_id)

    def delete(self, transcript_id: str) -> None:
        with get_session() as session:
            self._repository.delete_cascade(session, transcript_id)
        audit_event("transcript.delete", transcript_id=transcript_id)

    def purge_expired(self) -> int:
        """Delete transcripts older than ``transcript_retention_days``. Returns count."""
        days = settings.transcript_retention_days
        if days is None or days < 1:
            return 0
        cutoff = datetime.now(UTC) - timedelta(days=days)
        cutoff_naive = cutoff.replace(tzinfo=None)
        purged = 0
        with get_session() as session:
            ids = list(
                dict.fromkeys(
                    self._repository.list_ids_created_before(session, cutoff_naive)
                    + self._repository.list_ids_created_before(session, cutoff)
                )
            )
            for transcript_id in ids:
                try:
                    self._repository.delete_cascade(session, transcript_id)
                    purged += 1
                except TranscriptNotFoundError:
                    continue
        if purged:
            audit_event(
                "transcript.purge",
                purged_count=purged,
                retention_days=days,
            )
        return purged

    def update_speakers(
        self, transcript_id: str, speaker_updates: list[Speaker]
    ) -> TranscriptBundle:
        with get_session() as session:
            self._repository.update_speakers(session, transcript_id, speaker_updates)
            return self._repository.get_bundle(session, transcript_id)

    def update_turns(
        self, transcript_id: str, patches: list[dict]
    ) -> TranscriptBundle:
        if not patches:
            raise TranscriptValidationError("No turn patches provided")
        with get_session() as session:
            self._repository.update_turns(session, transcript_id, patches)
            self._repository.sync_raw_text_from_turns(session, transcript_id)
            bundle = self._repository.get_bundle(session, transcript_id)
            quotes = self._evidence_index.build_index_from_turns(
                transcript_id, bundle.turns
            )
            self._repository.replace_evidence_quotes(session, transcript_id, quotes)
            return self._repository.get_bundle(session, transcript_id)

    def rebuild_evidence_index(self, transcript_id: str) -> TranscriptBundle:
        with get_session() as session:
            bundle = self._repository.get_bundle(session, transcript_id)
            quotes = self._evidence_index.build_index_from_turns(
                transcript_id, bundle.turns
            )
            self._repository.replace_evidence_quotes(session, transcript_id, quotes)
            self._repository.sync_raw_text_from_turns(session, transcript_id)
            # Edits already clear ready; rebuild alone does not approve.
            return self._repository.get_bundle(session, transcript_id)

    def mark_ready(
        self,
        transcript_id: str,
        *,
        skip_review: bool = False,
    ) -> TranscriptBundle:
        with get_session() as session:
            bundle = self._repository.get_bundle(session, transcript_id)
            included = [t for t in bundle.turns if not t.excluded_from_analysis]
            if not included:
                raise TranscriptValidationError(
                    "Cannot mark ready: no turns included for analysis"
                )
            quotes = self._evidence_index.build_index_from_turns(
                transcript_id, bundle.turns
            )
            self._repository.replace_evidence_quotes(session, transcript_id, quotes)
            self._repository.sync_raw_text_from_turns(session, transcript_id)
            self._repository.set_preparation_state(
                session,
                transcript_id,
                analysis_ready=True,
                skip_review=skip_review,
                ready_at=utc_now().replace(tzinfo=None),
            )
            ready = self._repository.get_bundle(session, transcript_id)
        audit_event(
            "transcript.ready",
            transcript_id=transcript_id,
            skip_review=skip_review,
            quote_count=len(ready.evidence_quotes),
        )
        return ready

    def quality_warnings(self, bundle: TranscriptBundle) -> list[str]:
        warnings: list[str] = []
        included = [t for t in bundle.turns if not t.excluded_from_analysis]
        if not included:
            warnings.append("No turns are included for analysis.")
            return warnings
        if len(bundle.speakers) < 2:
            warnings.append("Only one speaker label is present.")
        blank = [t for t in included if not t.text.strip()]
        if blank:
            warnings.append(f"{len(blank)} included turn(s) have empty text.")
        short = [t for t in included if 0 < len(t.text.strip()) < 8]
        if short:
            warnings.append(f"{len(short)} included turn(s) are very short (< 8 chars).")
        unnamed = [
            s
            for s in bundle.speakers
            if not (s.display_name or s.label or "").strip()
        ]
        if unnamed:
            warnings.append("One or more speakers lack a display name.")
        if not bundle.evidence_quotes and included:
            warnings.append("Evidence index is empty; rebuild before analysis.")
        return warnings

    def ensure_ready_for_analysis(self, transcript_id: str) -> TranscriptBundle:
        bundle = self.get(transcript_id)
        if bundle.transcript.analysis_ready or bundle.transcript.skip_review:
            return bundle
        if settings.auto_mark_transcript_ready:
            return self.mark_ready(transcript_id)
        raise TranscriptNotReadyError(
            "Transcript is not marked Ready to Analyze. "
            "Review and approve it in Prepare, or skip review intentionally."
        )

    def ingest_from_audio(
        self,
        raw_text: str,
        language: str | None = None,
        title: str = "Audio transcription",
    ) -> TranscriptBundle:
        return self.ingest(
            raw_text=raw_text,
            source_type=SourceType.AUDIO,
            title=title,
            language=language,
        )


def _default_title(source_type: SourceType) -> str:
    return {
        SourceType.PASTE: "Pasted transcript",
        SourceType.FILE: "Uploaded transcript",
        SourceType.IMPORT: "Imported transcript",
        SourceType.AUDIO: "Audio transcription",
    }[source_type]


def _unique_labels(parsed_turns) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for turn in parsed_turns:
        if turn.speaker_label not in seen:
            seen.add(turn.speaker_label)
            labels.append(turn.speaker_label)
    return labels


transcript_service = TranscriptService()
