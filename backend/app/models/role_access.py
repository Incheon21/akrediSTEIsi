import uuid
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base

class RoleAccess(Base):
    __tablename__ = "role_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    api_path = Column(String(200), nullable=False)     # e.g., "/users/", "/posts/{id}"
    http_method = Column(String(10), nullable=False)   # e.g., "GET", "POST", "DELETE"

    role = relationship("Role", back_populates="accesses")

    def __repr__(self) -> str:
        return f"<RoleAccess id={self.id} role_id={self.role_id} api_path={self.api_path!r} method={self.http_method!r}>"
