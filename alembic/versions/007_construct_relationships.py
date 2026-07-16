"""Normalized construct relationships (v0.8 P3)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007_construct_relationships"
down_revision: Union[str, Sequence[str], None] = "006_normalized_constructs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "construct_relationships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("module_run_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("source_construct_source_id", sa.String(length=64), nullable=False),
        sa.Column("target_construct_source_id", sa.String(length=64), nullable=False),
        sa.Column("source_construct_row_id", sa.String(length=36), nullable=True),
        sa.Column("target_construct_row_id", sa.String(length=36), nullable=True),
        sa.Column("relationship_type", sa.String(length=128), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("ontology_resolved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ontology_warning", sa.Text(), nullable=True),
        sa.Column("link_warning", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["module_run_id"], ["module_runs.id"]),
    )
    op.create_index(
        "ix_construct_relationships_module_run_id",
        "construct_relationships",
        ["module_run_id"],
    )
    op.create_index(
        "ix_construct_relationships_workflow_run_id",
        "construct_relationships",
        ["workflow_run_id"],
    )

    op.create_table(
        "construct_relationship_evidence_quotes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("relationship_id", sa.String(length=36), nullable=False),
        sa.Column("quote_id", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["relationship_id"], ["construct_relationships.id"]),
    )
    op.create_index(
        "ix_construct_relationship_evidence_quotes_relationship_id",
        "construct_relationship_evidence_quotes",
        ["relationship_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_construct_relationship_evidence_quotes_relationship_id",
        table_name="construct_relationship_evidence_quotes",
    )
    op.drop_table("construct_relationship_evidence_quotes")
    op.drop_index(
        "ix_construct_relationships_workflow_run_id",
        table_name="construct_relationships",
    )
    op.drop_index(
        "ix_construct_relationships_module_run_id",
        table_name="construct_relationships",
    )
    op.drop_table("construct_relationships")
