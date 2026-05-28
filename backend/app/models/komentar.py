import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Komentar(Base):
    __tablename__ = "komentar"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_akreditasi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("target_akreditasi.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    isi_komentar = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    target_akreditasi = relationship("TargetAkreditasi", backref="komentar_list")
    user = relationship("User")
