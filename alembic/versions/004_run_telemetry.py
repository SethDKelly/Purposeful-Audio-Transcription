"""Add module/workflow telemetry columns (v0.7 P6)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_run_telemetry"
down_revision: Union[str, Sequence[str], None] = "003_module_validation_warnings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("module_runs", sa.Column("telemetry", sa.Text(), nullable=True))
    op.add_column(
        "workflow_runs",
        sa.Column("telemetry_summary", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("workflow_runs", "telemetry_summary")
    op.drop_column("module_runs", "telemetry")
