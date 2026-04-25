import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ProgramStudi(Base):
    __tablename__ = "program_studi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kode = Column(String(20), unique=True, nullable=False)  # kode prodi
    nama = Column(String(200), nullable=False)  # nama program studi
    jenjang = Column(String(10), nullable=False)  # S1, S2, S3, D3, D4
    fakultas = Column(String(200), nullable=True)
    perguruan_tinggi = Column(String(200), nullable=True)  # PT name for Menu!H7
    akreditasi = Column(String(50), nullable=True)  # A, B, C, Unggul, Baik Sekali, etc.
    no_sk_ban_pt = Column(String(100), nullable=True)  # for Menu!H67
    tanggal_akreditasi = Column(DateTime(timezone=True), nullable=True)
    tanggal_kadaluarsa = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="aktif")  # aktif, tidak aktif

    # Extended identity fields (Menu sheet + profile page)
    alamat = Column(Text, nullable=True)
    kota = Column(String(100), nullable=True)
    kode_pos = Column(String(10), nullable=True)
    nomor_telepon = Column(String(30), nullable=True)
    email = Column(String(200), nullable=True)
    website = Column(String(300), nullable=True)
    no_sk_pendirian_pt = Column(String(100), nullable=True)
    tanggal_sk_pendirian_pt = Column(DateTime(timezone=True), nullable=True)
    pejabat_sk_pendirian_pt = Column(String(200), nullable=True)
    no_sk_pembukaan_ps = Column(String(100), nullable=True)
    tanggal_sk_pembukaan_ps = Column(DateTime(timezone=True), nullable=True)
    pejabat_sk_pembukaan_ps = Column(String(200), nullable=True)
    tahun_pertama_menerima_mahasiswa = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    users = relationship("User", back_populates="program_studi")
    lkps_submissions = relationship("LkpsSubmission", back_populates="program_studi")
    target_akreditasi = relationship("TargetAkreditasi", back_populates="program_studi")
