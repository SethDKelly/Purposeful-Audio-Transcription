"""Add safety_events and evaluation_runs tables (v2.0 foundation)."""

from alembic import op
import sqlalchemy as sa

revision = "012_safety_events_evaluation_runs"
down_revision = "011_safety_mode"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "safety_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("transcript_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("categories_json", sa.Text(), nullable=True),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("fixture_id", sa.String(length=64), nullable=True),
        sa.Column("module_id", sa.String(length=128), nullable=True),
        sa.Column("gate_passed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("summary_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("evaluation_runs")
    op.drop_table("safety_events")
