import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Kriteria(Base):
    __tablename__ = "kriteria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kode = Column(String(20), unique=True, nullable=False)  # e.g. "C1", "C2"
    nama = Column(String(200), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    indikator = relationship("Indikator", back_populates="kriteria")
