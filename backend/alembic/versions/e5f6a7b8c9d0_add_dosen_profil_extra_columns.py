"""add missing columns to lkps_dosen_profil (sertifikasi, keinsinyuran, mk diampu)

Revision ID: e5f6a7b8c9d0
Revises: d4e7f1a2b3c8
Create Date: 2026-04-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e7f1a2b3c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lkps_dosen_profil", sa.Column("bidang_sertifikasi", sa.String(300), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("lembaga_penerbit_sertifikasi", sa.String(300), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("skip", sa.String(100), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("stri", sa.String(100), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("mk_diampu_ps_diakreditasi", sa.Text(), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("kesesuaian_bidang_mk", sa.String(50), nullable=True))
    op.add_column("lkps_dosen_profil", sa.Column("mk_diampu_ps_lain", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("lkps_dosen_profil", "mk_diampu_ps_lain")
    op.drop_column("lkps_dosen_profil", "kesesuaian_bidang_mk")
    op.drop_column("lkps_dosen_profil", "mk_diampu_ps_diakreditasi")
    op.drop_column("lkps_dosen_profil", "stri")
    op.drop_column("lkps_dosen_profil", "skip")
    op.drop_column("lkps_dosen_profil", "lembaga_penerbit_sertifikasi")
    op.drop_column("lkps_dosen_profil", "bidang_sertifikasi")
