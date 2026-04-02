import uuid

from sqlalchemy import Column, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base

class EvidenceCriteria(Base):
    __tablename__ = "evidence_criteria"

    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), primary_key=True)
    criteria = Column(UUID(as_uuid=True), ForeignKey("criteria.id"), primary_key=True)

    evidence = relationship("Evidence", back_populates="program_studi")
    program_studi = relationship("ProgramStudi", back_populates="evidence")
