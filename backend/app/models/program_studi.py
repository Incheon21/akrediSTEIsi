import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    users = relationship("User", back_populates="program_studi")
    lkps_submissions = relationship("LkpsSubmission", back_populates="program_studi")
