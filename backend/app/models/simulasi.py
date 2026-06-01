import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class MatriksAkreditasi(Base):
    __tablename__ = "matriks_akreditasi"

    id = Column(Integer, primary_key=True, index=True)
    lembaga = Column(String, index=True)  # e.g. "TEKNIK"
    jenjang = Column(String, index=True)  # e.g. "SARJANA"

    komponen = relationship("KomponenPenilaian", back_populates="matriks")


class KomponenPenilaian(Base):
    __tablename__ = "komponen_penilaian"

    id = Column(Integer, primary_key=True, index=True)
    matriks_id = Column(Integer, ForeignKey("matriks_akreditasi.id"))
    nama = Column(String)  # e.g. "Input", "Proses", "Output"
    bobot = Column(Float)

    matriks = relationship("MatriksAkreditasi", back_populates="komponen")
    indikator = relationship("IndikatorSimulasi", back_populates="komponen")


class IndikatorSimulasi(Base):
    __tablename__ = "indikator_simulasi"

    id = Column(Integer, primary_key=True, index=True)
    komponen_id = Column(Integer, ForeignKey("komponen_penilaian.id"))
    kode_indikator = Column(String)
    nama_indikator = Column(String)
    tipe_evaluasi = Column(
        String
    )  # e.g. "DIRECT_SCORE", "LINEAR_SCALE", "LESS_IS_BETTER"
    konfigurasi_rumus = Column(JSON)

    komponen = relationship("KomponenPenilaian", back_populates="indikator")


class SkorManualSimulasi(Base):
    __tablename__ = "skor_manual_simulasi"
    __table_args__ = (UniqueConstraint("submission_id", "kode_indikator"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("lkps_submission.id"), nullable=False)
    kode_indikator = Column(String, nullable=False)
    skor = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
