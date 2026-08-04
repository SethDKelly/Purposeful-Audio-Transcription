"""Seed admin user ollioxenhomefree@gmail.com (invite-only auth)."""

from alembic import op
import sqlalchemy as sa

revision = "017_seed_admin_user"
down_revision = "016_relationship_evidence_fields"
branch_labels = None
depends_on = None

ADMIN_EMAIL = "ollioxenhomefree@gmail.com"
ADMIN_ID = "00000000-0000-4000-a000-000000000001"


def upgrade() -> None:
    users = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("email", sa.String),
        sa.column("display_name", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("last_login_at", sa.DateTime),
        sa.column("is_active", sa.Boolean),
        sa.column("is_admin", sa.Boolean),
    )
    conn = op.get_bind()
    existing = conn.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    ).fetchone()
    if existing:
        conn.execute(
            sa.text(
                "UPDATE users SET is_admin = true, is_active = true "
                "WHERE email = :email"
            ),
            {"email": ADMIN_EMAIL},
        )
    else:
        op.execute(
            users.insert().values(
                id=ADMIN_ID,
                email=ADMIN_EMAIL,
                display_name="Admin",
                created_at=sa.func.current_timestamp(),
                last_login_at=None,
                is_active=True,
                is_admin=True,
            )
        )


def downgrade() -> None:
    # Keep the user row; only clear admin if it was the seed id.
    op.execute(
        sa.text(
            "UPDATE users SET is_admin = false "
            "WHERE id = :id AND email = :email"
        ),
        {"id": ADMIN_ID, "email": ADMIN_EMAIL},
    )
