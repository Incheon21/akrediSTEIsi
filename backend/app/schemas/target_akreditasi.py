from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class SetTargetScoreRequest(BaseModel):
    prodi_id: UUID
    target_skor: float
    tahun_akreditasi: int

class SetDeadlineRequest(BaseModel):
    prodi_id: UUID
    deadline: datetime
    tahun_akreditasi: int

class TargetAkreditasiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    program_studi_id: UUID
    tahun_akreditasi: int
    target_skor: float
    deadline: date
    notifikasi_aktif: bool
    is_aktif: bool
    created_at: datetime
    updated_at: datetime
