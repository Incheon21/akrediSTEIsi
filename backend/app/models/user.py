import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nama = Column(String(200), nullable=False)
    nip = Column(String(50), nullable=True, unique=True)
    is_active = Column(Boolean, default=True)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    program_studi_id = Column(
        UUID(as_uuid=True), ForeignKey("program_studi.id"), nullable=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    role = relationship("Role", back_populates="users")
    program_studi = relationship("ProgramStudi", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
