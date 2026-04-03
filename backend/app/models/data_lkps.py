import uuid
from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class DataLKPS(Base):
    __tablename__ = "data_lkps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_akreditasi_id = Column(UUID(as_uuid=True), ForeignKey("target_akreditasi.id"), nullable=False)
    indikator_id = Column(UUID(as_uuid=True), ForeignKey("indikator.id"), nullable=False)
    
    nilai_capaian = Column(Float, nullable=True)
    status_validasi = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    target_akreditasi = relationship("TargetAkreditasi", back_populates="data_lkps")
    indikator = relationship("Indikator", back_populates="data_lkps")
