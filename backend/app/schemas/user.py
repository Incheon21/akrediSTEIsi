from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.program_studi import ProgramStudiResponse
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    email: EmailStr
    nama: str
    nip: str | None = None


class UserCreate(UserBase):
    password: str
    role_id: UUID
    program_studi_id: UUID | None = None


class UserUpdate(BaseModel):
    email: str | None = None
    nama: str | None = None
    nip: str | None = None
    password: str | None = None
    is_active: bool | None = None
    role_id: UUID | None = None
    program_studi_id: UUID | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    nama: str
    nip: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role_id: UUID
    program_studi_id: UUID | None = None
    role: RoleResponse | None = None
    program_studi: ProgramStudiResponse | None = None
