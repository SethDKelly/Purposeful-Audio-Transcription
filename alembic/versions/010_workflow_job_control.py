"""Add workflow run job control fields (cancel, attempts)."""

from alembic import op
import sqlalchemy as sa

revision = "010_workflow_job_control"
down_revision = "009_finding_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_runs",
        sa.Column("cancel_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "workflow_runs",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("workflow_runs", "attempt_count")
    op.drop_column("workflow_runs", "cancel_requested")
