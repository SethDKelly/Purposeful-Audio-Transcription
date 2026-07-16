"""Normalized constructs tables (v0.8 P2)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "006_normalized_constructs"
down_revision: Union[str, Sequence[str], None] = "005_normalized_findings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "constructs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("module_run_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("ontology_type", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("ontology_resolved", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ontology_warning", sa.Text(), nullable=True),
        sa.Column("merged_into_id", sa.String(length=36), nullable=True),
        sa.Column("is_canonical", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("convergence_score", sa.String(length=32), nullable=True),
        sa.Column("convergence_rationale_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["module_run_id"], ["module_runs.id"]),
    )
    op.create_index("ix_constructs_module_run_id", "constructs", ["module_run_id"])
    op.create_index("ix_constructs_workflow_run_id", "constructs", ["workflow_run_id"])
    op.create_index("ix_constructs_merged_into_id", "constructs", ["merged_into_id"])

    op.create_table(
        "construct_evidence_quotes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("construct_id", sa.String(length=36), nullable=False),
        sa.Column("quote_id", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["construct_id"], ["constructs.id"]),
    )
    op.create_index(
        "ix_construct_evidence_quotes_construct_id",
        "construct_evidence_quotes",
        ["construct_id"],
    )

    op.create_table(
        "construct_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("construct_id", sa.String(length=36), nullable=False),
        sa.Column("module_run_id", sa.String(length=36), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("source_construct_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["construct_id"], ["constructs.id"]),
    )
    op.create_index(
        "ix_construct_sources_construct_id",
        "construct_sources",
        ["construct_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_construct_sources_construct_id", table_name="construct_sources")
    op.drop_table("construct_sources")
    op.drop_index(
        "ix_construct_evidence_quotes_construct_id",
        table_name="construct_evidence_quotes",
    )
    op.drop_table("construct_evidence_quotes")
    op.drop_index("ix_constructs_merged_into_id", table_name="constructs")
    op.drop_index("ix_constructs_workflow_run_id", table_name="constructs")
    op.drop_index("ix_constructs_module_run_id", table_name="constructs")
    op.drop_table("constructs")
