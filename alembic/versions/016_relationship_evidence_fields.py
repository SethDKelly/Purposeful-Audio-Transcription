"""Add rationale and alternative_explanations to construct_relationships (phase 008)."""

from alembic import op
import sqlalchemy as sa

revision = "016_relationship_evidence_fields"
down_revision = "015_evidence_snapshots_and_versioning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "construct_relationships",
        sa.Column("rationale", sa.Text(), nullable=True),
    )
    op.add_column(
        "construct_relationships",
        sa.Column("alternative_explanations_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("construct_relationships", "alternative_explanations_json")
    op.drop_column("construct_relationships", "rationale")
