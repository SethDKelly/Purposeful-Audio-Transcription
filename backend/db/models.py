from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class TranscriptRow(Base):
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(32))
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    analysis_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    ready_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    skip_review: Mapped[bool] = mapped_column(Boolean, default=False)

    speakers: Mapped[list["SpeakerRow"]] = relationship(back_populates="transcript")
    turns: Mapped[list["TurnRow"]] = relationship(back_populates="transcript")
    evidence_quotes: Mapped[list["EvidenceQuoteRow"]] = relationship(
        back_populates="transcript"
    )


class SpeakerRow(Base):
    __tablename__ = "speakers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    label: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    transcript: Mapped["TranscriptRow"] = relationship(back_populates="speakers")


class TurnRow(Base):
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    speaker_id: Mapped[str] = mapped_column(ForeignKey("speakers.id"))
    turn_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    start_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    excluded_from_analysis: Mapped[bool] = mapped_column(Boolean, default=False)

    transcript: Mapped["TranscriptRow"] = relationship(back_populates="turns")


class EvidenceQuoteRow(Base):
    __tablename__ = "evidence_quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    turn_id: Mapped[str] = mapped_column(ForeignKey("turns.id"))
    speaker_id: Mapped[str] = mapped_column(ForeignKey("speakers.id"))
    quote_index: Mapped[int] = mapped_column(Integer)
    quote_id: Mapped[str] = mapped_column(String(16))
    text: Mapped[str] = mapped_column(Text)
    context_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_after: Mapped[str | None] = mapped_column(Text, nullable=True)

    transcript: Mapped["TranscriptRow"] = relationship(back_populates="evidence_quotes")


class ModuleRunRow(Base):
    __tablename__ = "module_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    module_id: Mapped[str] = mapped_column(String(128))
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    workflow_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    module_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    compiler_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    prompt_template_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_flags: Mapped[str | None] = mapped_column(Text, nullable=True)
    telemetry: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WorkflowRunRow(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(128))
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    status: Mapped[str] = mapped_column(String(32))
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    telemetry_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class SynthesisReportRow(Base):
    __tablename__ = "synthesis_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(String(36), unique=True)
    report_json: Mapped[str] = mapped_column(Text)
    safety_flags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class FindingRow(Base):
    """Normalized finding row (v0.8). Raw JSON remains on module_runs for audit."""

    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(64))
    module_run_id: Mapped[str] = mapped_column(ForeignKey("module_runs.id"), index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    module_id: Mapped[str] = mapped_column(String(128))
    module_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(32))
    limitations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    construct_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class FindingEvidenceQuoteRow(Base):
    __tablename__ = "finding_evidence_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    finding_id: Mapped[str] = mapped_column(ForeignKey("findings.id"), index=True)
    quote_id: Mapped[str] = mapped_column(String(16))
    position: Mapped[int] = mapped_column(Integer, default=0)


class FindingAlternativeExplanationRow(Base):
    __tablename__ = "finding_alternative_explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    finding_id: Mapped[str] = mapped_column(ForeignKey("findings.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0)
