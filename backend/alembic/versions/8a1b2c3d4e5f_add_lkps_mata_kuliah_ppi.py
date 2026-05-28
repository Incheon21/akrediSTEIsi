"""add lkps mata kuliah ppi

Revision ID: 8a1b2c3d4e5f
Revises: 7b6a5c4d3e2f
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8a1b2c3d4e5f"
down_revision: Union[str, None] = "7b6a5c4d3e2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lkps_pppi_disiplin",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("disiplin", sa.String(length=300), nullable=False),
        sa.Column("diselenggarakan", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "disiplin"),
    )
    op.create_table(
        "lkps_mata_kuliah_ppi",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("mata_kuliah", sa.String(length=300), nullable=True),
        sa.Column("bobot_sks", sa.Numeric(4, 1), nullable=True),
        sa.Column("konversi_teori_jam", sa.Numeric(6, 1), nullable=True),
        sa.Column("konversi_praktik_jam", sa.Numeric(6, 1), nullable=True),
        sa.Column("dokumen_rps", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("lkps_mata_kuliah_ppi")
    op.drop_table("lkps_pppi_disiplin")
