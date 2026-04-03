import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    judul = Column(String(255), nullable=False)
    deskripsi = Column(Text, nullable=True)
    url_file = Column(String(500), nullable=False)
    tipe_file = Column(String(50), nullable=True)

    # Flag: True = evidence milik bersama (semua prodi bisa lihat & pakai)
    is_global = Column(Boolean, default=False, nullable=False)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    prodi_list = relationship("EvidenceProdi", back_populates="evidence", cascade="all, delete-orphan")
    indikator_list = relationship("EvidenceIndikator", back_populates="evidence", cascade="all, delete-orphan")


class EvidenceProdi(Base):
    __tablename__ = "evidence_prodi"

    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True)
    prodi_id = Column(UUID(as_uuid=True), ForeignKey("program_studi.id", ondelete="CASCADE"), primary_key=True)

    evidence = relationship("Evidence", back_populates="prodi_list")
    prodi = relationship("ProgramStudi")


class EvidenceIndikator(Base):
    __tablename__ = "evidence_indikator"

    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True)
    indikator_id = Column(UUID(as_uuid=True), ForeignKey("indikator.id", ondelete="CASCADE"), primary_key=True)
    target_akreditasi_id = Column(UUID(as_uuid=True), ForeignKey("target_akreditasi.id", ondelete="CASCADE"), nullable=False)

    evidence = relationship("Evidence", back_populates="indikator_list")
    indikator = relationship("Indikator")
    target_akreditasi = relationship("TargetAkreditasi")
