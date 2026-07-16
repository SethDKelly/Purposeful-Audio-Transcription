"""Add module_run validation_warnings for soft construct coverage (v0.7 P4)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_module_validation_warnings"
down_revision: Union[str, Sequence[str], None] = "002_transcript_preparation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "module_runs",
        sa.Column("validation_warnings", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("module_runs", "validation_warnings")
