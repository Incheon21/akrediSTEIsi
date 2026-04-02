import uuid

from sqlalchemy import Column, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base

class EvidenceProdi(Base):
    __tablename__ = "evidence_prodi"

    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), primary_key=True)
    prodi_id = Column(UUID(as_uuid=True), ForeignKey("program_studi.id"), primary_key=True)

    evidence = relationship("Evidence", back_populates="program_studi")
    prodi = relationship("prodi", back_populates="evidence")
