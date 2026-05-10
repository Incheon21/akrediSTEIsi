"""add_notifikasi

Revision ID: 7b6a5c4d3e2f
Revises: 9f2a1c3d4e5f
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7b6a5c4d3e2f"
down_revision: Union[str, None] = "9f2a1c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifikasi",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_studi_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_akreditasi_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_key", sa.String(length=200), nullable=False),
        sa.Column("kategori", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("judul", sa.String(length=200), nullable=False),
        sa.Column("pesan", sa.Text(), nullable=False),
        sa.Column("href", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["program_studi_id"], ["program_studi.id"]),
        sa.ForeignKeyConstraint(["target_akreditasi_id"], ["target_akreditasi.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "source_key"),
    )
    op.create_index("ix_notifikasi_user_id", "notifikasi", ["user_id"], unique=False)
    op.create_index("ix_notifikasi_is_read", "notifikasi", ["is_read"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notifikasi_is_read", table_name="notifikasi")
    op.drop_index("ix_notifikasi_user_id", table_name="notifikasi")
    op.drop_table("notifikasi")
