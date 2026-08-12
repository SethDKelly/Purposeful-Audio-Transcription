"""Add evidence_type and span_text for concise evidence (phase 004)."""

from alembic import op
import sqlalchemy as sa

from backend.db.migration_helpers import column_exists

revision = "014_evidence_precision"
down_revision = "013_email_auth_and_ownership"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not column_exists("evidence_quotes", "evidence_type"):
        op.add_column(
            "evidence_quotes",
            sa.Column(
                "evidence_type",
                sa.String(length=32),
                nullable=False,
                server_default="atomic_quote",
            ),
        )
    if not column_exists("evidence_quotes", "span_text"):
        op.add_column(
            "evidence_quotes",
            sa.Column("span_text", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("evidence_quotes", "span_text")
    op.drop_column("evidence_quotes", "evidence_type")
