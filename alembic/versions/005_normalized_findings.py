"""Normalized findings tables (v0.8 P1)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_normalized_findings"
down_revision: Union[str, Sequence[str], None] = "004_run_telemetry"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("module_run_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_run_id", sa.String(length=36), nullable=True),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("module_version", sa.String(length=32), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=True),
        sa.Column("construct_ids_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["module_run_id"], ["module_runs.id"]),
    )
    op.create_index("ix_findings_module_run_id", "findings", ["module_run_id"])
    op.create_index("ix_findings_workflow_run_id", "findings", ["workflow_run_id"])

    op.create_table(
        "finding_evidence_quotes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("finding_id", sa.String(length=36), nullable=False),
        sa.Column("quote_id", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"]),
    )
    op.create_index(
        "ix_finding_evidence_quotes_finding_id",
        "finding_evidence_quotes",
        ["finding_id"],
    )

    op.create_table(
        "finding_alternative_explanations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("finding_id", sa.String(length=36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"]),
    )
    op.create_index(
        "ix_finding_alternative_explanations_finding_id",
        "finding_alternative_explanations",
        ["finding_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finding_alternative_explanations_finding_id",
        table_name="finding_alternative_explanations",
    )
    op.drop_table("finding_alternative_explanations")
    op.drop_index(
        "ix_finding_evidence_quotes_finding_id",
        table_name="finding_evidence_quotes",
    )
    op.drop_table("finding_evidence_quotes")
    op.drop_index("ix_findings_workflow_run_id", table_name="findings")
    op.drop_index("ix_findings_module_run_id", table_name="findings")
    op.drop_table("findings")
