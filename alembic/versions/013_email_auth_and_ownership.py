"""Add email auth tables and owner_user_id columns (phase 003)."""

from alembic import op
import sqlalchemy as sa

from backend.db.migration_helpers import (
    column_exists,
    fk_exists,
    index_exists,
    table_exists,
)

revision = "013_email_auth_and_ownership"
down_revision = "012_safety_events_evaluation_runs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("display_name", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("last_login_at", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if not index_exists("ix_users_email"):
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if not table_exists("login_codes"):
        op.create_table(
            "login_codes",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("code_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("request_ip_hash", sa.String(length=64), nullable=True),
        )
    if not index_exists("ix_login_codes_email"):
        op.create_index("ix_login_codes_email", "login_codes", ["email"])

    if not table_exists("user_sessions"):
        op.create_table(
            "user_sessions",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("session_token_hash", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("last_seen_at", sa.DateTime(), nullable=True),
            sa.Column("user_agent_hash", sa.String(length=64), nullable=True),
            sa.Column("ip_hash", sa.String(length=64), nullable=True),
        )
    if not index_exists("ix_user_sessions_user_id"):
        op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    if not index_exists("ix_user_sessions_session_token_hash"):
        op.create_index(
            "ix_user_sessions_session_token_hash",
            "user_sessions",
            ["session_token_hash"],
            unique=True,
        )

    if not table_exists("auth_audit_events"):
        op.create_table(
            "auth_audit_events",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("actor_user_id", sa.String(length=36), nullable=True),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("resource_type", sa.String(length=64), nullable=True),
            sa.Column("resource_id", sa.String(length=64), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    if not index_exists("ix_auth_audit_events_actor_user_id"):
        op.create_index(
            "ix_auth_audit_events_actor_user_id",
            "auth_audit_events",
            ["actor_user_id"],
        )

    for table in (
        "transcripts",
        "cases",
        "workflow_runs",
        "finding_feedback",
        "evaluation_runs",
    ):
        if not column_exists(table, "owner_user_id"):
            op.add_column(
                table,
                sa.Column("owner_user_id", sa.String(length=36), nullable=True),
            )
        index_name = f"ix_{table}_owner_user_id"
        if not index_exists(index_name):
            op.create_index(index_name, table, ["owner_user_id"])
        fk_name = f"fk_{table}_owner_user_id_users"
        if not fk_exists(fk_name):
            op.create_foreign_key(
                fk_name,
                table,
                "users",
                ["owner_user_id"],
                ["id"],
            )


def downgrade() -> None:
    for table in (
        "evaluation_runs",
        "finding_feedback",
        "workflow_runs",
        "cases",
        "transcripts",
    ):
        op.drop_constraint(f"fk_{table}_owner_user_id_users", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_owner_user_id", table_name=table)
        op.drop_column(table, "owner_user_id")

    op.drop_index("ix_auth_audit_events_actor_user_id", table_name="auth_audit_events")
    op.drop_table("auth_audit_events")
    op.drop_index("ix_user_sessions_session_token_hash", table_name="user_sessions")
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("ix_login_codes_email", table_name="login_codes")
    op.drop_table("login_codes")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
