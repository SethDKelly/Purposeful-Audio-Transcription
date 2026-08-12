"""Add transcript versions and bind evidence/workflow runs (phase 005)."""

from alembic import op
import sqlalchemy as sa

from alembic.idempotent import column_exists, index_exists, table_exists

revision = "015_evidence_snapshots_and_versioning"
down_revision = "014_evidence_precision"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("transcript_versions"):
        op.create_table(
            "transcript_versions",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("transcript_id", sa.String(length=36), nullable=False),
            sa.Column("version_number", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
            sa.Column("source_type", sa.String(length=32), nullable=True),
            sa.Column("change_summary", sa.String(length=255), nullable=True),
            sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.ForeignKeyConstraint(["transcript_id"], ["transcripts.id"]),
            sa.UniqueConstraint(
                "transcript_id",
                "version_number",
                name="uq_transcript_versions_transcript_number",
            ),
        )
    if not index_exists("ix_transcript_versions_transcript_id"):
        op.create_index(
            "ix_transcript_versions_transcript_id",
            "transcript_versions",
            ["transcript_id"],
        )

    if not column_exists("transcripts", "current_version_id"):
        op.add_column(
            "transcripts",
            sa.Column("current_version_id", sa.String(length=36), nullable=True),
        )

    if not column_exists("evidence_quotes", "transcript_version_id"):
        op.add_column(
            "evidence_quotes",
            sa.Column("transcript_version_id", sa.String(length=36), nullable=True),
        )
    if not column_exists("workflow_runs", "transcript_version_id"):
        op.add_column(
            "workflow_runs",
            sa.Column("transcript_version_id", sa.String(length=36), nullable=True),
        )

    conn = op.get_bind()
    version_count = conn.execute(
        sa.text("SELECT COUNT(*) FROM transcript_versions")
    ).scalar()
    if not version_count:
        transcripts = conn.execute(
            sa.text("SELECT id, created_at, source_type FROM transcripts")
        ).fetchall()
        for transcript_id, created_at, source_type in transcripts:
            version_id = _new_id()
            conn.execute(
                sa.text(
                    "INSERT INTO transcript_versions "
                    "(id, transcript_id, version_number, created_at, created_by_user_id, "
                    "source_type, change_summary, is_current) "
                    "VALUES (:id, :transcript_id, 1, :created_at, NULL, :source_type, "
                    ":change_summary, 1)"
                ),
                {
                    "id": version_id,
                    "transcript_id": transcript_id,
                    "created_at": created_at,
                    "source_type": source_type,
                    "change_summary": "Backfill version 1",
                },
            )
            conn.execute(
                sa.text(
                    "UPDATE transcripts SET current_version_id = :version_id "
                    "WHERE id = :transcript_id"
                ),
                {"version_id": version_id, "transcript_id": transcript_id},
            )
            conn.execute(
                sa.text(
                    "UPDATE evidence_quotes SET transcript_version_id = :version_id "
                    "WHERE transcript_id = :transcript_id"
                ),
                {"version_id": version_id, "transcript_id": transcript_id},
            )
            conn.execute(
                sa.text(
                    "UPDATE workflow_runs SET transcript_version_id = :version_id "
                    "WHERE transcript_id = :transcript_id"
                ),
                {"version_id": version_id, "transcript_id": transcript_id},
            )

    if not index_exists("ix_evidence_quotes_transcript_version_id"):
        with op.batch_alter_table("evidence_quotes") as batch:
            batch.create_index(
                "ix_evidence_quotes_transcript_version_id",
                ["transcript_version_id"],
            )
    if not index_exists("uq_evidence_quotes_version_quote_id"):
        with op.batch_alter_table("evidence_quotes") as batch:
            batch.create_index(
                "uq_evidence_quotes_version_quote_id",
                ["transcript_version_id", "quote_id"],
                unique=True,
            )
    if not index_exists("ix_workflow_runs_transcript_version_id"):
        with op.batch_alter_table("workflow_runs") as batch:
            batch.create_index(
                "ix_workflow_runs_transcript_version_id",
                ["transcript_version_id"],
            )


def downgrade() -> None:
    with op.batch_alter_table("workflow_runs") as batch:
        batch.drop_index("ix_workflow_runs_transcript_version_id")
    with op.batch_alter_table("evidence_quotes") as batch:
        batch.drop_index("uq_evidence_quotes_version_quote_id")
        batch.drop_index("ix_evidence_quotes_transcript_version_id")
    op.drop_column("workflow_runs", "transcript_version_id")
    op.drop_column("evidence_quotes", "transcript_version_id")
    op.drop_column("transcripts", "current_version_id")
    op.drop_index("ix_transcript_versions_transcript_id", table_name="transcript_versions")
    op.drop_table("transcript_versions")


def _new_id() -> str:
    import uuid

    return str(uuid.uuid4())
