"""Add transcript preparation fields (v0.7 P2)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_transcript_preparation"
down_revision: Union[str, Sequence[str], None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transcripts",
        sa.Column(
            "analysis_ready",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "transcripts",
        sa.Column("ready_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column(
            "skip_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "turns",
        sa.Column(
            "excluded_from_analysis",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("turns", "excluded_from_analysis")
    op.drop_column("transcripts", "skip_review")
    op.drop_column("transcripts", "ready_at")
    op.drop_column("transcripts", "analysis_ready")
