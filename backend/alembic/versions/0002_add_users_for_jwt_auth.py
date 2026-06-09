"""Add users table for JWT authentication.

Revision ID: 0002_add_users_for_jwt_auth
Revises: 0001_initial_schema
Create Date: 2026-06-09
"""

from uuid import UUID

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_add_users_for_jwt_auth"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


DEFAULT_ADMIN_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_ADMIN_EMAIL = "admin@cowork.local"
DEFAULT_ADMIN_PASSWORD_HASH = (
    "scrypt$16384$8$1$ABEiM0RVZneImaq7zN3u_w==$"
    "1JYTd0AsdtPK-Zibl2MGJxpbBBwDrRdvPERwtbQWzbCbubuE3qSb_wqPetVqChSV"
    "hRILYMTeUU7GGZn5KLWSqw=="
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    users_table = sa.table(
        "users",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("email", sa.String(length=255)),
        sa.column("password_hash", sa.String(length=255)),
        sa.column("is_active", sa.Boolean()),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": DEFAULT_ADMIN_USER_ID,
                "email": DEFAULT_ADMIN_EMAIL,
                "password_hash": DEFAULT_ADMIN_PASSWORD_HASH,
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("users")
