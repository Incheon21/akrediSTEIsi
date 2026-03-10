from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProgramStudiBase(BaseModel):
    kode: str
    nama: str
    jenjang: str
    fakultas: Optional[str] = None
    akreditasi: Optional[str] = None
    tanggal_akreditasi: Optional[datetime] = None
    tanggal_kadaluarsa: Optional[datetime] = None
    status: Optional[str] = "aktif"


class ProgramStudiCreate(ProgramStudiBase):
    pass


class ProgramStudiUpdate(BaseModel):
    kode: Optional[str] = None
    nama: Optional[str] = None
    jenjang: Optional[str] = None
    fakultas: Optional[str] = None
    akreditasi: Optional[str] = None
    tanggal_akreditasi: Optional[datetime] = None
    tanggal_kadaluarsa: Optional[datetime] = None
    status: Optional[str] = None


class ProgramStudiResponse(ProgramStudiBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
