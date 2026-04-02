import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Indikator(Base):
    __tablename__ = "indikator"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kriteria_id = Column(UUID(as_uuid=True), ForeignKey("kriteria.id"), nullable=False)
    kode_indikator = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=False)
    tipe_input = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    kriteria = relationship("Kriteria", back_populates="indikator")
    evidence_list = relationship("EvidenceIndikator", back_populates="indikator")
    data_lkps = relationship("DataLKPS", back_populates="indikator")
    narasi_led = relationship("NarasiLED", back_populates="indikator")
