import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Notifikasi(Base):
    __tablename__ = "notifikasi"
    __table_args__ = (UniqueConstraint("user_id", "source_key"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    program_studi_id = Column(UUID(as_uuid=True), ForeignKey("program_studi.id"), nullable=True)
    target_akreditasi_id = Column(UUID(as_uuid=True), ForeignKey("target_akreditasi.id"), nullable=True)
    source_key = Column(String(200), nullable=False)
    kategori = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, default="info")
    judul = Column(String(200), nullable=False)
    pesan = Column(Text, nullable=False)
    href = Column(String(500), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    program_studi = relationship("ProgramStudi")
    target_akreditasi = relationship("TargetAkreditasi")
