from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LEDSaveRequest(BaseModel):
    target_akreditasi_id: UUID = Field(
        ..., description="ID target akreditasi yang aktif"
    )
    indikator_id: UUID = Field(..., description="ID indikator LED")
    narasi: str = Field(
        ..., min_length=1, description="Isi narasi LED (tidak boleh kosong)"
    )


class LEDResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    target_akreditasi_id: UUID
    indikator_id: UUID
    narasi: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LEDSaveResponse(BaseModel):
    message: str
    data: LEDResponse


class LEDBatchResponse(BaseModel):
    data: dict[str, LEDResponse]
