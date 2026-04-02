import uuid

from sqlalchemy import Column, DateTime, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)

    description = Column(Text)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploader = relationship("User", back_populates="evidence")

    criterias = relationship(
        "Criteria",
        secondary="evidence_criteria",
        backref="evidence"
    )

    program_studi = relationship(
        "EvidenceProdi",
        back_populates="evidence",
        cascade="all, delete-orphan"
    )
