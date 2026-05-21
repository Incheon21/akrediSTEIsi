from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserKomentar(BaseModel):
    id: UUID
    nama: str
    role: str


class KomentarCreate(BaseModel):
    isi_komentar: str = Field(..., min_length=1, description="Isi komentar dari pimpinan")


class KomentarUpdate(BaseModel):
    isi_komentar: str = Field(..., min_length=1)


class KomentarResponse(BaseModel):
    id: UUID
    target_akreditasi_id: UUID
    user_id: Optional[UUID] = None
    isi_komentar: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserKomentar] = None

    class Config:
        from_attributes = True
