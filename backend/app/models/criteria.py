import uuid

from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base

class Criteria(Base):
    __tablename__ = "criteria"

    id = Column(UUID(as_uuid=True), primary_key=True)
    number = Column(String(50), nullable=False, unique=True)
    name = Column(String(255))  # optional description/title
