"""Add rationale and alternative_explanations to construct_relationships (phase 008)."""

from alembic import op
import sqlalchemy as sa

from backend.db.migration_helpers import column_exists

revision = "016_relationship_evidence_fields"
down_revision = "015_evidence_snapshots_and_versioning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not column_exists("construct_relationships", "rationale"):
        op.add_column(
            "construct_relationships",
            sa.Column("rationale", sa.Text(), nullable=True),
        )
    if not column_exists("construct_relationships", "alternative_explanations_json"):
        op.add_column(
            "construct_relationships",
            sa.Column("alternative_explanations_json", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("construct_relationships", "alternative_explanations_json")
    op.drop_column("construct_relationships", "rationale")
