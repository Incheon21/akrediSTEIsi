"""add_skor_manual_simulasi

Revision ID: 9f2a1c3d4e5f
Revises: e0fc705b4cfc
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9f2a1c3d4e5f"
down_revision: Union[str, None] = "e0fc705b4cfc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skor_manual_simulasi",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kode_indikator", sa.String(), nullable=False),
        sa.Column("skor", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "kode_indikator"),
    )
    op.create_index(
        "ix_skor_manual_simulasi_submission_id",
        "skor_manual_simulasi",
        ["submission_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_skor_manual_simulasi_submission_id", table_name="skor_manual_simulasi")
    op.drop_table("skor_manual_simulasi")
