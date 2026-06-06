"""Create initial schema with no-overlap exclusion constraint.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-06-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_table(
        "spaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("hourly_rate > 0", name="ck_space_hourly_rate_gt_zero"),
        sa.CheckConstraint("capacity > 0", name="ck_space_capacity_gt_zero"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "time_slot",
            postgresql.TSTZRANGE(),
            sa.Computed("tstzrange(start_at, end_at, '[)')", persisted=True),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("end_at > start_at", name="ck_reservation_end_after_start"),
        sa.CheckConstraint(
            "total_price >= 0",
            name="ck_reservation_total_price_gte_zero",
        ),
        sa.ForeignKeyConstraint(["space_id"], ["spaces.id"], ondelete="RESTRICT"),
        postgresql.ExcludeConstraint(
            ("space_id", "="),
            ("time_slot", "&&"),
            where=sa.text("status IN ('PENDIENTE', 'CONFIRMADA')"),
            using="gist",
            name="reservations_no_overlap",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("spaces")
