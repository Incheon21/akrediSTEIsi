"""
LKPS (Laporan Kinerja Program Studi) database models.

All section tables reference lkps_submission as their parent.
Column names and structure mirror the official LAM-Tek LKPS Excel template.
"""

import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

class LkpsTemplate(Base):
    """Stores uploaded LKPS Excel template files. Multiple versions supported."""
    __tablename__ = "lkps_template"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(50), nullable=False, unique=True)  # e.g. "2024-v1"
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # path on server / object storage key
    is_active = Column(Boolean, default=True, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    submissions = relationship("LkpsSubmission", back_populates="template")


# ---------------------------------------------------------------------------
# Submission envelope
# ---------------------------------------------------------------------------

class LkpsSubmission(Base):
    """One submission per program studi per accreditation cycle (TS year)."""
    __tablename__ = "lkps_submission"
    __table_args__ = (UniqueConstraint("program_studi_id", "tahun_ts"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_studi_id = Column(UUID(as_uuid=True), ForeignKey("program_studi.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("lkps_template.id"), nullable=True)
    tahun_ts = Column(Integer, nullable=False)  # e.g. 2024; TS-1=2023, TS-2=2022
    status = Column(String(20), default="draft")  # draft | submitted | reviewed | approved
    nama_pengusul = Column(String(200), nullable=True)  # Menu!S69
    tanggal_pengajuan = Column(Date, nullable=True)      # Menu!S71
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    program_studi = relationship("ProgramStudi", back_populates="lkps_submissions")
    template = relationship("LkpsTemplate", back_populates="submissions")
    section_progress = relationship("LkpsSectionProgress", back_populates="submission", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------

class LkpsSectionProgress(Base):
    """Tracks fill-completion for each LKPS section within a submission."""
    __tablename__ = "lkps_section_progress"
    __table_args__ = (UniqueConstraint("submission_id", "section_code"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    section_code = Column(String(20), nullable=False)  # e.g. "1","2a1","3b","4d","6c1"
    status = Column(String(20), default="not_started")  # not_started | in_progress | completed
    completion_pct = Column(Integer, default=0)          # 0-100
    notes = Column(Text, nullable=True)
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    submission = relationship("LkpsSubmission", back_populates="section_progress")


# ---------------------------------------------------------------------------
# Section 1 – Visi Misi Tujuan Strategi (VMTS)
# ---------------------------------------------------------------------------

class LkpsVmts(Base):
    """Sheet '1': VMTS PT, UPPS, dan Visi Keilmuan PS."""
    __tablename__ = "lkps_vmts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=False)         # row number in template (1-9)
    jenis_vmts = Column(String(100), nullable=True)  # "VMTS PT" / "VMTS UPPS" / "Visi Keilmuan PS"
    pernyataan = Column(Text, nullable=True)
    no_sk = Column(String(100), nullable=True)
    link_dokumen = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 2a – Kerjasama Tridharma (sheets 2a1, 2a2, 2a3 unified)
# ---------------------------------------------------------------------------

class LkpsKerjasama(Base):
    """Sheets '2a1','2a2','2a3': Kerjasama Tridharma – pendidikan, penelitian, pkm."""
    __tablename__ = "lkps_kerjasama"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    jenis = Column(String(20), nullable=False)          # pendidikan | penelitian | pkm
    lembaga_mitra = Column(String(500), nullable=True)
    tingkat = Column(String(20), nullable=True)         # internasional | nasional | lokal
    judul_kegiatan = Column(Text, nullable=True)
    manfaat = Column(Text, nullable=True)
    tanggal_awal = Column(Date, nullable=True)          # col H – drives K-column formula
    tanggal_akhir = Column(Date, nullable=True)         # col I
    # durasi & status are formula-computed in template; stored here for dashboard queries only
    durasi_tahun = Column(Numeric(5, 2), nullable=True)
    status_kerjasama = Column(String(20), nullable=True)
    bukti_kerjasama = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 2b – Penggunaan Dana
# ---------------------------------------------------------------------------

class LkpsPenggunaanDana(Base):
    """Sheet '2b': Dana operasional per jenis penggunaan.

    ``kode`` identifies the fixed row in the template.
    Average columns (F, J) are formula-computed and never written.
    """
    __tablename__ = "lkps_penggunaan_dana"
    __table_args__ = (UniqueConstraint("submission_id", "kode"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    # kode maps to a fixed row: biaya_dosen→7, biaya_tendik→8, biaya_op_pembelajaran→9,
    # biaya_op_tidak_langsung→10, biaya_praktik_ppi→11, biaya_investasi→12,
    # biaya_kemahasiswaan→13, biaya_penelitian→15, biaya_pkm→16
    kode = Column(String(50), nullable=False)
    upps_ts2 = Column(BigInteger, default=0)
    upps_ts1 = Column(BigInteger, default=0)
    upps_ts = Column(BigInteger, default=0)
    ps_ts2 = Column(BigInteger, default=0)
    ps_ts1 = Column(BigInteger, default=0)
    ps_ts = Column(BigInteger, default=0)


# ---------------------------------------------------------------------------
# Section 3a1 – Kurikulum dan Rencana Pembelajaran
# ---------------------------------------------------------------------------

class LkpsKurikulum(Base):
    """Sheet '3a1': Daftar mata kuliah dalam kurikulum."""
    __tablename__ = "lkps_kurikulum"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)
    kode_mk = Column(String(50), nullable=True)
    nama_mk = Column(String(300), nullable=True)
    kompetensi = Column(Text, nullable=True)
    sks_kuliah = Column(Numeric(4, 1), nullable=True)
    sks_seminar = Column(Numeric(4, 1), nullable=True)
    sks_praktikum = Column(Numeric(4, 1), nullable=True)
    konversi_jam = Column(Numeric(6, 1), nullable=True)
    dokumen_rps = Column(Text, nullable=True)
    unit_penyelenggara = Column(String(100), nullable=True)  # Universitas | Fakultas | Prodi


# ---------------------------------------------------------------------------
# Section 3a3 – Integrasi Penelitian/PkM dalam Pembelajaran
# ---------------------------------------------------------------------------

class LkpsIntegrasiPenelitian(Base):
    """Sheet '3a3': Integrasi kegiatan penelitian/PkM ke dalam mata kuliah."""
    __tablename__ = "lkps_integrasi_penelitian"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    nama_dosen = Column(String(300), nullable=True)
    judul_penelitian_pkm = Column(Text, nullable=True)
    mata_kuliah = Column(String(300), nullable=True)
    bentuk_integrasi = Column(String(200), nullable=True)
    tahun_ts2 = Column(Boolean, default=False)
    tahun_ts1 = Column(Boolean, default=False)
    tahun_ts = Column(Boolean, default=False)
    kesesuaian_peta_jalan = Column(String(50), nullable=True)  # Sesuai | Tidak Sesuai
    bukti_sahih = Column(Text, nullable=True)
    kesesuaian_rps = Column(String(100), nullable=True)


# ---------------------------------------------------------------------------
# Section 3a4 – Mata Kuliah Basic Science & Matematika
# ---------------------------------------------------------------------------

class LkpsMkBasicScience(Base):
    """Sheet '3a4': Mata kuliah basic science dan matematika (Sarjana/Sarjana Terapan)."""
    __tablename__ = "lkps_mk_basic_science"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_mk = Column(String(300), nullable=True)
    semester = Column(Integer, nullable=True)
    jumlah_sks = Column(Numeric(4, 1), nullable=True)


# ---------------------------------------------------------------------------
# Section 3a5 – Capstone Design
# ---------------------------------------------------------------------------

class LkpsCapstoneDesign(Base):
    """Sheet '3a5': Capstone design dalam proses pembelajaran."""
    __tablename__ = "lkps_capstone_design"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_mk_pendukung = Column(String(300), nullable=True)
    sks_pendukung = Column(Numeric(4, 1), nullable=True)
    nama_mk_capstone = Column(String(300), nullable=True)
    sks_capstone = Column(Numeric(4, 1), nullable=True)
    semester = Column(Integer, nullable=True)
    cakupan_bahasan = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 3b – Penelitian DTPS (aggregate count)
# ---------------------------------------------------------------------------

class LkpsPenelitianSummary(Base):
    """Sheet '3b': Jumlah judul penelitian DTPS per sumber pembiayaan."""
    __tablename__ = "lkps_penelitian_summary"
    __table_args__ = (UniqueConstraint("submission_id", "kode_sumber"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    # kode_sumber: perguruan_tinggi_mandiri→row9, dalam_negeri→row10, luar_negeri→row11
    kode_sumber = Column(String(50), nullable=False)
    ts2 = Column(Integer, default=0)
    ts1 = Column(Integer, default=0)
    ts = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 3c – PkM DTPS (aggregate count)
# ---------------------------------------------------------------------------

class LkpsPkmSummary(Base):
    """Sheet '3c': Jumlah judul PkM DTPS per sumber pembiayaan."""
    __tablename__ = "lkps_pkm_summary"
    __table_args__ = (UniqueConstraint("submission_id", "kode_sumber"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    kode_sumber = Column(String(50), nullable=False)
    ts2 = Column(Integer, default=0)
    ts1 = Column(Integer, default=0)
    ts = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 4a – Profil Dosen
# ---------------------------------------------------------------------------

class LkpsDosenProfil(Base):
    """Sheet '4a': Profil DTPS (Dosen Tetap Program Studi)."""
    __tablename__ = "lkps_dosen_profil"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    nidn_nidk = Column(String(50), nullable=True)
    kategori = Column(String(50), nullable=True)   # DT | DTT | Industri
    prodi_sarjana = Column(String(300), nullable=True)
    prodi_magister = Column(String(300), nullable=True)
    prodi_doktor = Column(String(300), nullable=True)
    bidang_keahlian = Column(Text, nullable=True)
    perusahaan_industri = Column(String(300), nullable=True)
    kesesuaian_kompetensi = Column(String(50), nullable=True)  # Sesuai | Tidak Sesuai
    jabatan_akademik = Column(String(100), nullable=True)
    no_sertifikat_pendidik = Column(String(100), nullable=True)


# ---------------------------------------------------------------------------
# Section 4b – Tenaga Kependidikan
# ---------------------------------------------------------------------------

class LkpsTenagaKependidikan(Base):
    """Sheet '4b': Laboran/Teknisi/Administrator Sistem."""
    __tablename__ = "lkps_tenaga_kependidikan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama = Column(String(300), nullable=True)
    pendidikan_terakhir = Column(String(10), nullable=True)  # S3|S2|S1|D4|D3|D2|D1|SMA_SMK
    sertifikat_kompetensi = Column(Text, nullable=True)
    unit_kerja = Column(String(100), nullable=True)  # UPPS | Program Studi | Institusi


# ---------------------------------------------------------------------------
# Section 4c – Beban Kerja Dosen Tetap
# ---------------------------------------------------------------------------

class LkpsBebanKerjaDosen(Base):
    """Sheet '4c': BK dosen tetap per semester dalam sks."""
    __tablename__ = "lkps_beban_kerja_dosen"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    dtps = Column(Boolean, default=False)  # is this DTPS?
    bk_ps_diakreditasi = Column(Numeric(5, 1), nullable=True)
    bk_ps_lain_pt = Column(Numeric(5, 1), nullable=True)
    bk_ps_luar_pt = Column(Numeric(5, 1), nullable=True)
    bk_penelitian = Column(Numeric(5, 1), nullable=True)
    bk_pkm = Column(Numeric(5, 1), nullable=True)
    bk_tugas_tambahan = Column(Numeric(5, 1), nullable=True)
    # jumlah_per_tahun & jumlah_per_semester are formula-computed in template


# ---------------------------------------------------------------------------
# Section 4d/4e/6e1/6e2 – Publikasi Ilmiah (aggregate, fixed rows)
# ---------------------------------------------------------------------------

class LkpsPublikasiIlmiah(Base):
    """Sheets '4d','4e','6e1','6e2': Jumlah publikasi per jenis per tahun.

    ``sumber``: dtps | mahasiswa
    ``jenis_program``: akademik | vokasi
    ``kode_publikasi`` maps to a fixed template row (mapper handles the mapping).
    Total row (Jumlah) is formula-computed and never written.
    """
    __tablename__ = "lkps_publikasi_ilmiah"
    __table_args__ = (UniqueConstraint("submission_id", "sumber", "jenis_program", "kode_publikasi"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    sumber = Column(String(20), nullable=False)          # dtps | mahasiswa
    jenis_program = Column(String(20), nullable=False)   # akademik | vokasi
    # kode_publikasi values: jurnal_nasional_tidak_terakreditasi, jurnal_nasional_terakreditasi,
    # jurnal_internasional, jurnal_internasional_bereputasi, prosiding_nasional,
    # prosiding_internasional_tidak_terindeks, prosiding_internasional_terindeks,
    # pagelaran_wilayah, pagelaran_nasional, pagelaran_internasional (vokasi only)
    kode_publikasi = Column(String(100), nullable=False)
    ts2 = Column(Integer, default=0)
    ts1 = Column(Integer, default=0)
    ts = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 4f-1 to 4f-4 / 6e3-1 to 6e3-4 – Luaran Penelitian & PkM
# ---------------------------------------------------------------------------

class LkpsLuaranPenelitian(Base):
    """Sheets '4f-*' and '6e3-*': Luaran penelitian/PkM (HKI, teknologi, buku).

    ``sumber``: dtps | mahasiswa
    ``jenis_luaran``: paten | hak_cipta | teknologi | buku
    """
    __tablename__ = "lkps_luaran_penelitian"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    sumber = Column(String(20), nullable=False)       # dtps | mahasiswa
    jenis_luaran = Column(String(20), nullable=False) # paten | hak_cipta | teknologi | buku
    judul = Column(Text, nullable=True)
    tanggal = Column(Date, nullable=True)
    # paten fields
    nomor_paten = Column(String(100), nullable=True)
    # hak_cipta fields
    nomor_hki = Column(String(100), nullable=True)
    # teknologi fields
    status_tkt = Column(String(20), nullable=True)    # TKT 1..9
    nomor_sertifikat_tkt = Column(String(100), nullable=True)
    # buku fields
    nomor_isbn = Column(String(100), nullable=True)
    # mahasiswa-specific
    status_mahasiswa = Column(String(30), nullable=True)  # Registered|Granted|Komersial
    keterangan = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 4g / 6e4 – Produk/Jasa yang Diadopsi
# ---------------------------------------------------------------------------

class LkpsProdukJasa(Base):
    """Sheets '4g','6e4': Produk/jasa yang diadopsi industri/masyarakat.

    ``sumber``: dtps | mahasiswa
    """
    __tablename__ = "lkps_produk_jasa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    sumber = Column(String(20), nullable=False)   # dtps | mahasiswa
    nama_pembuat = Column(String(300), nullable=True)  # nama DTPS or nama mahasiswa
    nama_produk_jasa = Column(String(300), nullable=True)
    deskripsi = Column(Text, nullable=True)
    bukti = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 4h – Kinerja DTPS (kompetitif)
# ---------------------------------------------------------------------------

class LkpsKinerjaDtps(Base):
    """Sheet '4h': Jumlah publikasi internasional bereputasi per dosen per TS."""
    __tablename__ = "lkps_kinerja_dtps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    ts2 = Column(Integer, default=0)
    ts1 = Column(Integer, default=0)
    ts = Column(Integer, default=0)
    keterangan = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 4i – Sitasi DTPS
# ---------------------------------------------------------------------------

class LkpsSitasiDtps(Base):
    """Sheet '4i': Karya ilmiah DTPS yang disitasi dalam 3 tahun terakhir."""
    __tablename__ = "lkps_sitasi_dtps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    judul_artikel = Column(Text, nullable=True)
    jumlah_sitasi = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 4j – Rekognisi DTPS
# ---------------------------------------------------------------------------

class LkpsRekognisiDtps(Base):
    """Sheet '4j': Pengakuan/rekognisi DTPS (visiting lecturer, keynote, dll)."""
    __tablename__ = "lkps_rekognisi_dtps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    bidang_keahlian = Column(String(200), nullable=True)
    rekognisi = Column(Text, nullable=True)
    bukti_pendukung = Column(Text, nullable=True)
    tingkat = Column(String(20), nullable=True)  # wilayah | nasional | internasional
    tahun = Column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Section 4k – Pembimbing Lapangan (PPI)
# ---------------------------------------------------------------------------

class LkpsPembimbingLapangan(Base):
    """Sheet '4k': Pembimbing lapangan Program Profesi Insinyur."""
    __tablename__ = "lkps_pembimbing_lapangan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama = Column(String(300), nullable=True)
    industri = Column(String(300), nullable=True)
    bidang_keinsinyuran = Column(String(200), nullable=True)
    pengalaman_kerja_tahun = Column(Integer, nullable=True)
    pendidikan_tinggi = Column(String(50), nullable=True)
    kategori_sip = Column(String(10), nullable=True)  # IPM | IPU
    nomor_sip = Column(String(100), nullable=True)
    tanggal_berakhir_sip = Column(Date, nullable=True)
    jumlah_bimbingan_3tahun = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 5a – Prasarana & Sarana
# ---------------------------------------------------------------------------

class LkpsPrasarana(Base):
    """Sheet '5a': Prasarana dan peralatan utama laboratorium/ruang."""
    __tablename__ = "lkps_prasarana"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_prasarana = Column(String(300), nullable=True)
    jumlah_prasarana = Column(Integer, nullable=True)
    nama_sarana = Column(String(300), nullable=True)
    jumlah_standar_minimal = Column(Integer, nullable=True)
    jumlah_dimiliki = Column(Integer, nullable=True)
    kepemilikan = Column(String(20), nullable=True)   # sendiri | sewa
    kondisi = Column(String(20), nullable=True)        # terawat | tidak_terawat
    logbook = Column(String(20), nullable=True)        # ada | tidak_ada (vokasi only)


# ---------------------------------------------------------------------------
# Section 5b – Dokumen K3L
# ---------------------------------------------------------------------------

class LkpsK3lDokumen(Base):
    """Sheet '5b': Dokumen Keselamatan, Kesehatan Kerja dan Lingkungan."""
    __tablename__ = "lkps_k3l_dokumen"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    jenis_dokumen = Column(String(300), nullable=True)
    jumlah = Column(Integer, nullable=True)
    riwayat_pengesahan = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 5c – Fasilitas K3L
# ---------------------------------------------------------------------------

class LkpsK3lFasilitas(Base):
    """Sheet '5c': Fasilitas K3L di UPPS."""
    __tablename__ = "lkps_k3l_fasilitas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    nama_sarana = Column(String(300), nullable=True)
    fungsi = Column(String(300), nullable=True)
    jumlah_unit = Column(Integer, nullable=True)
    kondisi = Column(String(20), nullable=True)  # terawat | tidak_terawat


# ---------------------------------------------------------------------------
# Section 6a – Jumlah Mahasiswa Aktif & Asing
# ---------------------------------------------------------------------------

class LkpsMahasiswaAktif(Base):
    """Sheet '6a': Jumlah mahasiswa reguler dan asing per program studi."""
    __tablename__ = "lkps_mahasiswa_aktif"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    program_studi_nama = Column(String(300), nullable=True)
    prodi_diakreditasi = Column(Boolean, default=False)
    aktif_ts2 = Column(Integer, default=0)
    aktif_ts1 = Column(Integer, default=0)
    aktif_ts = Column(Integer, default=0)
    asing_fulltime_ts2 = Column(Integer, default=0)
    asing_fulltime_ts1 = Column(Integer, default=0)
    asing_fulltime_ts = Column(Integer, default=0)
    asing_parttime_ts2 = Column(Integer, default=0)
    asing_parttime_ts1 = Column(Integer, default=0)
    asing_parttime_ts = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 6b – IPK Lulusan
# ---------------------------------------------------------------------------

class LkpsIpkLulusan(Base):
    """Sheet '6b': IPK lulusan untuk TS-2, TS-1, TS."""
    __tablename__ = "lkps_ipk_lulusan"
    __table_args__ = (UniqueConstraint("submission_id", "periode"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    periode = Column(String(10), nullable=False)  # TS-2 | TS-1 | TS
    jumlah_lulusan = Column(Integer, default=0)
    ipk_min = Column(Numeric(4, 2), nullable=True)
    ipk_rata = Column(Numeric(4, 2), nullable=True)
    ipk_maks = Column(Numeric(4, 2), nullable=True)


# ---------------------------------------------------------------------------
# Section 6c – Prestasi Mahasiswa (6c1 akademik + 6c2 non-akademik)
# ---------------------------------------------------------------------------

class LkpsPrestasiMahasiswa(Base):
    """Sheets '6c1','6c2': Prestasi akademik dan non-akademik mahasiswa."""
    __tablename__ = "lkps_prestasi_mahasiswa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    jenis = Column(String(20), nullable=False)   # akademik | non_akademik
    no = Column(Integer, nullable=True)
    nama_kegiatan = Column(String(400), nullable=True)
    waktu_perolehan = Column(Date, nullable=True)
    tingkat = Column(String(20), nullable=True)  # lokal | nasional | internasional
    prestasi_dicapai = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 6d – Masa Studi Lulusan
# ---------------------------------------------------------------------------

class LkpsMasaStudi(Base):
    """Sheet '6d': Masa studi lulusan per jenis program dan tahun masuk."""
    __tablename__ = "lkps_masa_studi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    jenis_program = Column(String(20), nullable=True)  # D1|D2|D3|S1|S1Tr|S2|S2Tr|S3|S3Tr|PPI
    tahun_masuk = Column(String(10), nullable=True)    # e.g. "TS-4" or "2020"
    jumlah_masuk = Column(Integer, default=0)
    jumlah_lulus_tepat_waktu = Column(Integer, default=0)
    jumlah_lulus_terlambat = Column(Integer, default=0)
    jumlah_tidak_lulus = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 6f1 – Waktu Tunggu Lulusan
# ---------------------------------------------------------------------------

class LkpsWaktuTunggu(Base):
    """Sheet '6f1': Waktu tunggu mendapatkan pekerjaan setelah lulus."""
    __tablename__ = "lkps_waktu_tunggu"
    __table_args__ = (UniqueConstraint("submission_id", "jenis_program", "tahun_lulus"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    jenis_program = Column(String(20), nullable=True)
    tahun_lulus = Column(String(10), nullable=False)  # TS-2 | TS-1 | TS
    jumlah_lulusan = Column(Integer, default=0)
    jumlah_terlacak = Column(Integer, default=0)
    jumlah_dipesan_sebelum_lulus = Column(Integer, default=0)
    wt_lt_3bulan = Column(Integer, default=0)
    wt_3_6bulan = Column(Integer, default=0)
    wt_gt_6bulan = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 6f2 – Kesesuaian Bidang Kerja
# ---------------------------------------------------------------------------

class LkpsKesesuaianKerja(Base):
    """Sheet '6f2': Kesesuaian bidang kerja lulusan."""
    __tablename__ = "lkps_kesesuaian_kerja"
    __table_args__ = (UniqueConstraint("submission_id", "tahun_lulus"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    tahun_lulus = Column(String(10), nullable=False)  # TS-2 | TS-1 | TS
    jumlah_lulusan = Column(Integer, default=0)
    jumlah_terlacak = Column(Integer, default=0)
    kesesuaian_rendah = Column(Integer, default=0)
    kesesuaian_sedang = Column(Integer, default=0)
    kesesuaian_tinggi = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 6g1 – Tempat Kerja Lulusan
# ---------------------------------------------------------------------------

class LkpsTempatKerja(Base):
    """Sheet '6g1': Tingkat tempat kerja/wirausaha lulusan."""
    __tablename__ = "lkps_tempat_kerja"
    __table_args__ = (UniqueConstraint("submission_id", "tahun_lulus"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    tahun_lulus = Column(String(10), nullable=False)  # TS-2 | TS-1 | TS
    jumlah_lulusan = Column(Integer, default=0)
    jumlah_pengguna_tanggapan = Column(Integer, default=0)
    jumlah_terlacak = Column(Integer, default=0)
    bekerja_lokal = Column(Integer, default=0)
    bekerja_nasional = Column(Integer, default=0)
    bekerja_multinasional = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Section 6g2 – Kepuasan Pengguna Lulusan
# ---------------------------------------------------------------------------

class LkpsKepuasanPengguna(Base):
    """Sheet '6g2': Tingkat kepuasan pengguna lulusan."""
    __tablename__ = "lkps_kepuasan_pengguna"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    jenis_kemampuan = Column(String(300), nullable=True)
    sangat_baik = Column(Numeric(5, 2), nullable=True)  # percentage
    baik = Column(Numeric(5, 2), nullable=True)
    cukup = Column(Numeric(5, 2), nullable=True)
    kurang = Column(Numeric(5, 2), nullable=True)
    rencana_tindak_lanjut = Column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Section 6h1 / 6h2 / 6i – Penelitian/PkM yang Melibatkan Mahasiswa
# ---------------------------------------------------------------------------

class LkpsPenelitianMahasiswa(Base):
    """Sheets '6h1','6h2','6i': penelitian/tesis/PkM DTPS yang melibatkan mahasiswa.

    ``jenis``: penelitian | tesis_disertasi | pkm
    """
    __tablename__ = "lkps_penelitian_mahasiswa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    jenis = Column(String(30), nullable=False)   # penelitian | tesis_disertasi | pkm
    no = Column(Integer, nullable=True)
    nama_dosen = Column(String(300), nullable=True)
    tema_penelitian = Column(Text, nullable=True)
    nama_mahasiswa = Column(String(300), nullable=True)
    judul_kegiatan = Column(Text, nullable=True)
    tahun = Column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Section 7a – SPMI Dokumen
# ---------------------------------------------------------------------------

class LkpsSpmiDokumen(Base):
    """Sheet '7a': Ketersediaan dokumen Sistem Penjaminan Mutu Internal."""
    __tablename__ = "lkps_spmi_dokumen"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    jenis_dokumen = Column(Text, nullable=True)
    no_dokumen = Column(String(100), nullable=True)
    tanggal_dokumen = Column(Date, nullable=True)


# ---------------------------------------------------------------------------
# Section 7b – SPMI Pelaksanaan
# ---------------------------------------------------------------------------

class LkpsSpmiPelaksanaan(Base):
    """Sheet '7b': Dokumen pelaksanaan Sistem Penjaminan Mutu Internal (PPEPP)."""
    __tablename__ = "lkps_spmi_pelaksanaan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    no = Column(Integer, nullable=True)
    # Penetapan | Pelaksanaan | Evaluasi | Pengendalian | Peningkatan
    jenis_pelaksanaan = Column(String(50), nullable=True)
    link_dokumen = Column(Text, nullable=True)
    link_laporan_audit = Column(Text, nullable=True)
    link_laporan_rtm = Column(Text, nullable=True)
    link_dokumen_peningkatan = Column(Text, nullable=True)
