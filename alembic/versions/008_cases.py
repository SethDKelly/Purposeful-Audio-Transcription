"""Add cases and transcript case linkage (v0.9 P1)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "008_cases"
down_revision: Union[str, Sequence[str], None] = "007_construct_relationships"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.add_column("transcripts", sa.Column("case_id", sa.String(length=36), nullable=True))
    op.add_column(
        "transcripts", sa.Column("session_label", sa.String(length=128), nullable=True)
    )
    op.add_column("transcripts", sa.Column("session_date", sa.DateTime(), nullable=True))
    op.create_foreign_key(
        "fk_transcripts_case_id_cases",
        "transcripts",
        "cases",
        ["case_id"],
        ["id"],
    )
    op.create_index("ix_transcripts_case_id", "transcripts", ["case_id"])


def downgrade() -> None:
    op.drop_index("ix_transcripts_case_id", table_name="transcripts")
    op.drop_constraint("fk_transcripts_case_id_cases", "transcripts", type_="foreignkey")
    op.drop_column("transcripts", "session_date")
    op.drop_column("transcripts", "session_label")
    op.drop_column("transcripts", "case_id")
    op.drop_table("cases")
