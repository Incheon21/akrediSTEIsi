from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GetAllRolesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roles: list[RoleResponse]

class ProgramStudiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kode: str
    nama: str


class GetAllProgramStudiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    program_studi: list[ProgramStudiResponse]

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    nama: str
    nip: Optional[str] = None
    is_active: bool
    role: RoleResponse
    program_studi: Optional[ProgramStudiResponse] = None
    created_at: datetime
    updated_at: datetime


class GetAllUsersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: list[UserResponse]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    nama: str
    nip: Optional[str] = None
    is_active: bool = True
    role_id: UUID
    program_studi_id: Optional[UUID] = None


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    nama: Optional[str] = None
    nip: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[UUID] = None
    program_studi_id: Optional[UUID] = None
