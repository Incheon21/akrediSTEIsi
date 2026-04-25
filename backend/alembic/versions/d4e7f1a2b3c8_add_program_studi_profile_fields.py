"""add program_studi profile fields

Revision ID: d4e7f1a2b3c8
Revises: f1a92d4b7c10, b9c4d8e1f2a3
Create Date: 2026-04-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e7f1a2b3c8"
down_revision: Union[str, Sequence[str], None] = ("f1a92d4b7c10", "b9c4d8e1f2a3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("program_studi", sa.Column("alamat", sa.Text(), nullable=True))
    op.add_column("program_studi", sa.Column("kota", sa.String(100), nullable=True))
    op.add_column("program_studi", sa.Column("kode_pos", sa.String(10), nullable=True))
    op.add_column("program_studi", sa.Column("nomor_telepon", sa.String(30), nullable=True))
    op.add_column("program_studi", sa.Column("email", sa.String(200), nullable=True))
    op.add_column("program_studi", sa.Column("website", sa.String(300), nullable=True))
    op.add_column("program_studi", sa.Column("no_sk_pendirian_pt", sa.String(100), nullable=True))
    op.add_column("program_studi", sa.Column("tanggal_sk_pendirian_pt", sa.DateTime(timezone=True), nullable=True))
    op.add_column("program_studi", sa.Column("pejabat_sk_pendirian_pt", sa.String(200), nullable=True))
    op.add_column("program_studi", sa.Column("no_sk_pembukaan_ps", sa.String(100), nullable=True))
    op.add_column("program_studi", sa.Column("tanggal_sk_pembukaan_ps", sa.DateTime(timezone=True), nullable=True))
    op.add_column("program_studi", sa.Column("pejabat_sk_pembukaan_ps", sa.String(200), nullable=True))
    op.add_column("program_studi", sa.Column("tahun_pertama_menerima_mahasiswa", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("program_studi", "tahun_pertama_menerima_mahasiswa")
    op.drop_column("program_studi", "pejabat_sk_pembukaan_ps")
    op.drop_column("program_studi", "tanggal_sk_pembukaan_ps")
    op.drop_column("program_studi", "no_sk_pembukaan_ps")
    op.drop_column("program_studi", "pejabat_sk_pendirian_pt")
    op.drop_column("program_studi", "tanggal_sk_pendirian_pt")
    op.drop_column("program_studi", "no_sk_pendirian_pt")
    op.drop_column("program_studi", "website")
    op.drop_column("program_studi", "email")
    op.drop_column("program_studi", "nomor_telepon")
    op.drop_column("program_studi", "kode_pos")
    op.drop_column("program_studi", "kota")
    op.drop_column("program_studi", "alamat")
