"""Add safety_mode to workflow runs (v1.0 P5)."""

from alembic import op
import sqlalchemy as sa

revision = "011_safety_mode"
down_revision = "010_workflow_job_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_runs",
        sa.Column("safety_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("workflow_runs", "safety_mode")
