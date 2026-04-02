import uuid
from sqlalchemy import Column, Integer, Float, Date, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class TargetAkreditasi(Base):
    __tablename__ = "target_akreditasi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_studi_id = Column(UUID(as_uuid=True), ForeignKey("program_studi.id"), nullable=False)
    
    tahun_akreditasi = Column(Integer, nullable=False)
    target_skor = Column(Float, nullable=True)
    deadline = Column(Date, nullable=True)
    notifikasi_aktif = Column(Boolean, default=True)
    is_aktif = Column(Boolean, default=False) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    program_studi = relationship("ProgramStudi", back_populates="target_akreditasi")
    data_lkps = relationship("DataLKPS", back_populates="target_akreditasi")
    narasi_led = relationship("NarasiLED", back_populates="target_akreditasi")
