"""add lkps tables

Revision ID: a3f2b1c4d5e6
Revises: ec7f9ad03f45
Create Date: 2026-04-02 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3f2b1c4d5e6"
down_revision: Union[str, None] = "ec7f9ad03f45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # Extend program_studi with two new columns
    # -----------------------------------------------------------------------
    op.add_column("program_studi", sa.Column("perguruan_tinggi", sa.String(200), nullable=True))
    op.add_column("program_studi", sa.Column("no_sk_ban_pt", sa.String(100), nullable=True))

    # -----------------------------------------------------------------------
    # lkps_template
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_template",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("uploaded_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version"),
    )

    # -----------------------------------------------------------------------
    # lkps_submission
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_submission",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("program_studi_id", sa.UUID(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=True),
        sa.Column("tahun_ts", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=True, server_default="draft"),
        sa.Column("nama_pengusul", sa.String(200), nullable=True),
        sa.Column("tanggal_pengajuan", sa.Date(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["program_studi_id"], ["program_studi.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["lkps_template.id"]),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_studi_id", "tahun_ts"),
    )

    # -----------------------------------------------------------------------
    # lkps_section_progress
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_section_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("section_code", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=True, server_default="not_started"),
        sa.Column("completion_pct", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("last_updated_by", sa.UUID(), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["last_updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "section_code"),
    )

    # -----------------------------------------------------------------------
    # Section 1 – VMTS
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_vmts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("jenis_vmts", sa.String(100), nullable=True),
        sa.Column("pernyataan", sa.Text(), nullable=True),
        sa.Column("no_sk", sa.String(100), nullable=True),
        sa.Column("link_dokumen", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # -----------------------------------------------------------------------
    # Section 2 – Kerjasama + Dana
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_kerjasama",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("jenis", sa.String(20), nullable=False),
        sa.Column("lembaga_mitra", sa.String(500), nullable=True),
        sa.Column("tingkat", sa.String(20), nullable=True),
        sa.Column("judul_kegiatan", sa.Text(), nullable=True),
        sa.Column("manfaat", sa.Text(), nullable=True),
        sa.Column("tanggal_awal", sa.Date(), nullable=True),
        sa.Column("tanggal_akhir", sa.Date(), nullable=True),
        sa.Column("durasi_tahun", sa.Numeric(5, 2), nullable=True),
        sa.Column("status_kerjasama", sa.String(20), nullable=True),
        sa.Column("bukti_kerjasama", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_penggunaan_dana",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("kode", sa.String(50), nullable=False),
        sa.Column("upps_ts2", sa.BigInteger(), nullable=True, server_default="0"),
        sa.Column("upps_ts1", sa.BigInteger(), nullable=True, server_default="0"),
        sa.Column("upps_ts", sa.BigInteger(), nullable=True, server_default="0"),
        sa.Column("ps_ts2", sa.BigInteger(), nullable=True, server_default="0"),
        sa.Column("ps_ts1", sa.BigInteger(), nullable=True, server_default="0"),
        sa.Column("ps_ts", sa.BigInteger(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "kode"),
    )

    # -----------------------------------------------------------------------
    # Section 3 – Kurikulum, Integrasi, Basic Science, Capstone, Summaries
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_kurikulum",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("semester", sa.Integer(), nullable=True),
        sa.Column("kode_mk", sa.String(50), nullable=True),
        sa.Column("nama_mk", sa.String(300), nullable=True),
        sa.Column("kompetensi", sa.Text(), nullable=True),
        sa.Column("sks_kuliah", sa.Numeric(4, 1), nullable=True),
        sa.Column("sks_seminar", sa.Numeric(4, 1), nullable=True),
        sa.Column("sks_praktikum", sa.Numeric(4, 1), nullable=True),
        sa.Column("konversi_jam", sa.Numeric(6, 1), nullable=True),
        sa.Column("dokumen_rps", sa.Text(), nullable=True),
        sa.Column("unit_penyelenggara", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_integrasi_penelitian",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("judul_penelitian_pkm", sa.Text(), nullable=True),
        sa.Column("mata_kuliah", sa.String(300), nullable=True),
        sa.Column("bentuk_integrasi", sa.String(200), nullable=True),
        sa.Column("tahun_ts2", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("tahun_ts1", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("tahun_ts", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("kesesuaian_peta_jalan", sa.String(50), nullable=True),
        sa.Column("bukti_sahih", sa.Text(), nullable=True),
        sa.Column("kesesuaian_rps", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_mk_basic_science",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_mk", sa.String(300), nullable=True),
        sa.Column("semester", sa.Integer(), nullable=True),
        sa.Column("jumlah_sks", sa.Numeric(4, 1), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_capstone_design",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_mk_pendukung", sa.String(300), nullable=True),
        sa.Column("sks_pendukung", sa.Numeric(4, 1), nullable=True),
        sa.Column("nama_mk_capstone", sa.String(300), nullable=True),
        sa.Column("sks_capstone", sa.Numeric(4, 1), nullable=True),
        sa.Column("semester", sa.Integer(), nullable=True),
        sa.Column("cakupan_bahasan", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_penelitian_summary",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("kode_sumber", sa.String(50), nullable=False),
        sa.Column("ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "kode_sumber"),
    )

    op.create_table(
        "lkps_pkm_summary",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("kode_sumber", sa.String(50), nullable=False),
        sa.Column("ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "kode_sumber"),
    )

    # -----------------------------------------------------------------------
    # Section 4 – Dosen
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_dosen_profil",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("nidn_nidk", sa.String(50), nullable=True),
        sa.Column("kategori", sa.String(50), nullable=True),
        sa.Column("prodi_sarjana", sa.String(300), nullable=True),
        sa.Column("prodi_magister", sa.String(300), nullable=True),
        sa.Column("prodi_doktor", sa.String(300), nullable=True),
        sa.Column("bidang_keahlian", sa.Text(), nullable=True),
        sa.Column("perusahaan_industri", sa.String(300), nullable=True),
        sa.Column("kesesuaian_kompetensi", sa.String(50), nullable=True),
        sa.Column("jabatan_akademik", sa.String(100), nullable=True),
        sa.Column("no_sertifikat_pendidik", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_tenaga_kependidikan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama", sa.String(300), nullable=True),
        sa.Column("pendidikan_terakhir", sa.String(10), nullable=True),
        sa.Column("sertifikat_kompetensi", sa.Text(), nullable=True),
        sa.Column("unit_kerja", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_beban_kerja_dosen",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("dtps", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("bk_ps_diakreditasi", sa.Numeric(5, 1), nullable=True),
        sa.Column("bk_ps_lain_pt", sa.Numeric(5, 1), nullable=True),
        sa.Column("bk_ps_luar_pt", sa.Numeric(5, 1), nullable=True),
        sa.Column("bk_penelitian", sa.Numeric(5, 1), nullable=True),
        sa.Column("bk_pkm", sa.Numeric(5, 1), nullable=True),
        sa.Column("bk_tugas_tambahan", sa.Numeric(5, 1), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_publikasi_ilmiah",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("sumber", sa.String(20), nullable=False),
        sa.Column("jenis_program", sa.String(20), nullable=False),
        sa.Column("kode_publikasi", sa.String(100), nullable=False),
        sa.Column("ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "sumber", "jenis_program", "kode_publikasi"),
    )

    op.create_table(
        "lkps_luaran_penelitian",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("sumber", sa.String(20), nullable=False),
        sa.Column("jenis_luaran", sa.String(20), nullable=False),
        sa.Column("judul", sa.Text(), nullable=True),
        sa.Column("tanggal", sa.Date(), nullable=True),
        sa.Column("nomor_paten", sa.String(100), nullable=True),
        sa.Column("nomor_hki", sa.String(100), nullable=True),
        sa.Column("status_tkt", sa.String(20), nullable=True),
        sa.Column("nomor_sertifikat_tkt", sa.String(100), nullable=True),
        sa.Column("nomor_isbn", sa.String(100), nullable=True),
        sa.Column("status_mahasiswa", sa.String(30), nullable=True),
        sa.Column("keterangan", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_produk_jasa",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("sumber", sa.String(20), nullable=False),
        sa.Column("nama_pembuat", sa.String(300), nullable=True),
        sa.Column("nama_produk_jasa", sa.String(300), nullable=True),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("bukti", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_kinerja_dtps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ts", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("keterangan", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_sitasi_dtps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("judul_artikel", sa.Text(), nullable=True),
        sa.Column("jumlah_sitasi", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_rekognisi_dtps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("bidang_keahlian", sa.String(200), nullable=True),
        sa.Column("rekognisi", sa.Text(), nullable=True),
        sa.Column("bukti_pendukung", sa.Text(), nullable=True),
        sa.Column("tingkat", sa.String(20), nullable=True),
        sa.Column("tahun", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_pembimbing_lapangan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama", sa.String(300), nullable=True),
        sa.Column("industri", sa.String(300), nullable=True),
        sa.Column("bidang_keinsinyuran", sa.String(200), nullable=True),
        sa.Column("pengalaman_kerja_tahun", sa.Integer(), nullable=True),
        sa.Column("pendidikan_tinggi", sa.String(50), nullable=True),
        sa.Column("kategori_sip", sa.String(10), nullable=True),
        sa.Column("nomor_sip", sa.String(100), nullable=True),
        sa.Column("tanggal_berakhir_sip", sa.Date(), nullable=True),
        sa.Column("jumlah_bimbingan_3tahun", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # -----------------------------------------------------------------------
    # Section 5 – Sarana & K3L
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_prasarana",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_prasarana", sa.String(300), nullable=True),
        sa.Column("jumlah_prasarana", sa.Integer(), nullable=True),
        sa.Column("nama_sarana", sa.String(300), nullable=True),
        sa.Column("jumlah_standar_minimal", sa.Integer(), nullable=True),
        sa.Column("jumlah_dimiliki", sa.Integer(), nullable=True),
        sa.Column("kepemilikan", sa.String(20), nullable=True),
        sa.Column("kondisi", sa.String(20), nullable=True),
        sa.Column("logbook", sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_k3l_dokumen",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("jenis_dokumen", sa.String(300), nullable=True),
        sa.Column("jumlah", sa.Integer(), nullable=True),
        sa.Column("riwayat_pengesahan", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_k3l_fasilitas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_sarana", sa.String(300), nullable=True),
        sa.Column("fungsi", sa.String(300), nullable=True),
        sa.Column("jumlah_unit", sa.Integer(), nullable=True),
        sa.Column("kondisi", sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # -----------------------------------------------------------------------
    # Section 6 – Mahasiswa & Lulusan
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_mahasiswa_aktif",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("program_studi_nama", sa.String(300), nullable=True),
        sa.Column("prodi_diakreditasi", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("aktif_ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("aktif_ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("aktif_ts", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_fulltime_ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_fulltime_ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_fulltime_ts", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_parttime_ts2", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_parttime_ts1", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asing_parttime_ts", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_ipk_lulusan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("periode", sa.String(10), nullable=False),
        sa.Column("jumlah_lulusan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ipk_min", sa.Numeric(4, 2), nullable=True),
        sa.Column("ipk_rata", sa.Numeric(4, 2), nullable=True),
        sa.Column("ipk_maks", sa.Numeric(4, 2), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "periode"),
    )

    op.create_table(
        "lkps_prestasi_mahasiswa",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("jenis", sa.String(20), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_kegiatan", sa.String(400), nullable=True),
        sa.Column("waktu_perolehan", sa.Date(), nullable=True),
        sa.Column("tingkat", sa.String(20), nullable=True),
        sa.Column("prestasi_dicapai", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_masa_studi",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("jenis_program", sa.String(20), nullable=True),
        sa.Column("tahun_masuk", sa.String(10), nullable=True),
        sa.Column("jumlah_masuk", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_lulus_tepat_waktu", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_lulus_terlambat", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_tidak_lulus", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_waktu_tunggu",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("jenis_program", sa.String(20), nullable=True),
        sa.Column("tahun_lulus", sa.String(10), nullable=False),
        sa.Column("jumlah_lulusan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_terlacak", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_dipesan_sebelum_lulus", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("wt_lt_3bulan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("wt_3_6bulan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("wt_gt_6bulan", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "jenis_program", "tahun_lulus"),
    )

    op.create_table(
        "lkps_kesesuaian_kerja",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("tahun_lulus", sa.String(10), nullable=False),
        sa.Column("jumlah_lulusan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_terlacak", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("kesesuaian_rendah", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("kesesuaian_sedang", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("kesesuaian_tinggi", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "tahun_lulus"),
    )

    op.create_table(
        "lkps_tempat_kerja",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("tahun_lulus", sa.String(10), nullable=False),
        sa.Column("jumlah_lulusan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_pengguna_tanggapan", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("jumlah_terlacak", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("bekerja_lokal", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("bekerja_nasional", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("bekerja_multinasional", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id", "tahun_lulus"),
    )

    op.create_table(
        "lkps_kepuasan_pengguna",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("jenis_kemampuan", sa.String(300), nullable=True),
        sa.Column("sangat_baik", sa.Numeric(5, 2), nullable=True),
        sa.Column("baik", sa.Numeric(5, 2), nullable=True),
        sa.Column("cukup", sa.Numeric(5, 2), nullable=True),
        sa.Column("kurang", sa.Numeric(5, 2), nullable=True),
        sa.Column("rencana_tindak_lanjut", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_penelitian_mahasiswa",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("jenis", sa.String(30), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("nama_dosen", sa.String(300), nullable=True),
        sa.Column("tema_penelitian", sa.Text(), nullable=True),
        sa.Column("nama_mahasiswa", sa.String(300), nullable=True),
        sa.Column("judul_kegiatan", sa.Text(), nullable=True),
        sa.Column("tahun", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # -----------------------------------------------------------------------
    # Section 7 – SPMI
    # -----------------------------------------------------------------------
    op.create_table(
        "lkps_spmi_dokumen",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("jenis_dokumen", sa.Text(), nullable=True),
        sa.Column("no_dokumen", sa.String(100), nullable=True),
        sa.Column("tanggal_dokumen", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lkps_spmi_pelaksanaan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("no", sa.Integer(), nullable=True),
        sa.Column("jenis_pelaksanaan", sa.String(50), nullable=True),
        sa.Column("link_dokumen", sa.Text(), nullable=True),
        sa.Column("link_laporan_audit", sa.Text(), nullable=True),
        sa.Column("link_laporan_rtm", sa.Text(), nullable=True),
        sa.Column("link_dokumen_peningkatan", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["lkps_submission.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    for table in [
        "lkps_spmi_pelaksanaan", "lkps_spmi_dokumen",
        "lkps_penelitian_mahasiswa", "lkps_kepuasan_pengguna",
        "lkps_tempat_kerja", "lkps_kesesuaian_kerja", "lkps_waktu_tunggu",
        "lkps_masa_studi", "lkps_prestasi_mahasiswa", "lkps_ipk_lulusan",
        "lkps_mahasiswa_aktif", "lkps_k3l_fasilitas", "lkps_k3l_dokumen",
        "lkps_prasarana", "lkps_pembimbing_lapangan", "lkps_rekognisi_dtps",
        "lkps_sitasi_dtps", "lkps_kinerja_dtps", "lkps_produk_jasa",
        "lkps_luaran_penelitian", "lkps_publikasi_ilmiah",
        "lkps_beban_kerja_dosen", "lkps_tenaga_kependidikan", "lkps_dosen_profil",
        "lkps_pkm_summary", "lkps_penelitian_summary",
        "lkps_capstone_design", "lkps_mk_basic_science",
        "lkps_integrasi_penelitian", "lkps_kurikulum",
        "lkps_penggunaan_dana", "lkps_kerjasama", "lkps_vmts",
        "lkps_section_progress", "lkps_submission", "lkps_template",
    ]:
        op.drop_table(table)
    op.drop_column("program_studi", "no_sk_ban_pt")
    op.drop_column("program_studi", "perguruan_tinggi")
