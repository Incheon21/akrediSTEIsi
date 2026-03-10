from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.role import RoleResponse
from app.schemas.program_studi import ProgramStudiResponse


class UserBase(BaseModel):
    email: str
    nama: str
    nip: Optional[str] = None
    role_id: UUID
    program_studi_id: Optional[UUID] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    nama: Optional[str] = None
    nip: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[UUID] = None
    program_studi_id: Optional[UUID] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    nama: str
    nip: Optional[str] = None
    is_active: bool
    role_id: UUID
    program_studi_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleResponse] = None
    program_studi: Optional[ProgramStudiResponse] = None

    class Config:
        from_attributes = True
