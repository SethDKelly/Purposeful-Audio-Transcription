"""Finding feedback table (v0.9 P6)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "009_finding_feedback"
down_revision: Union[str, Sequence[str], None] = "008_cases"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "finding_feedback",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("finding_row_id", sa.String(length=36), nullable=True),
        sa.Column("finding_key", sa.String(length=256), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("transcript_id", sa.String(length=36), nullable=True),
        sa.Column("case_id", sa.String(length=36), nullable=True),
        sa.Column("rating", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["finding_row_id"], ["findings.id"]),
    )
    op.create_index("ix_finding_feedback_finding_key", "finding_feedback", ["finding_key"])
    op.create_index(
        "ix_finding_feedback_workflow_run_id", "finding_feedback", ["workflow_run_id"]
    )
    op.create_index(
        "ix_finding_feedback_finding_row_id", "finding_feedback", ["finding_row_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_finding_feedback_finding_row_id", table_name="finding_feedback")
    op.drop_index("ix_finding_feedback_workflow_run_id", table_name="finding_feedback")
    op.drop_index("ix_finding_feedback_finding_key", table_name="finding_feedback")
    op.drop_table("finding_feedback")
