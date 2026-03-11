from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgramStudiBase(BaseModel):
    kode: str
    nama: str
    jenjang: str
    fakultas: str | None = None
    akreditasi: str | None = None
    tanggal_akreditasi: datetime | None = None
    tanggal_kadaluarsa: datetime | None = None
    status: str | None = "aktif"


class ProgramStudiCreate(ProgramStudiBase):
    pass


class ProgramStudiUpdate(BaseModel):
    kode: str | None = None
    nama: str | None = None
    jenjang: str | None = None
    fakultas: str | None = None
    akreditasi: str | None = None
    tanggal_akreditasi: datetime | None = None
    tanggal_kadaluarsa: datetime | None = None
    status: str | None = None


class ProgramStudiResponse(ProgramStudiBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
