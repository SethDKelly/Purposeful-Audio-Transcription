import uuid

from backend.core.exceptions import TranscriptNotFoundError
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

        return bundle

    def get(self, transcript_id: str) -> TranscriptBundle:
        with get_session() as session:
            return self._repository.get_bundle(session, transcript_id)

    def update_speakers(
        self, transcript_id: str, speaker_updates: list[Speaker]
    ) -> TranscriptBundle:
        with get_session() as session:
            self._repository.update_speakers(session, transcript_id, speaker_updates)
            return self._repository.get_bundle(session, transcript_id)

    def ingest_from_whisper(
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
