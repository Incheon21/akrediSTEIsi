from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceBase(BaseModel):
    judul: str
    deskripsi: Optional[str] = None
    is_global: bool = False


class EvidenceCreate(EvidenceBase):
    """
    Schema for creating evidence.
    Note: In FastAPI, file uploads usually use Form() and UploadFile directly in the endpoint,
    but this schema can be used if metadata is sent as a JSON string or parsed from form fields.
    """

    pass


class EvidenceResponse(EvidenceBase):
    id: UUID
    url_file: str
    tipe_file: Optional[str] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceDetailResponse(EvidenceResponse):
    """
    Extended response that could include related uploader info or linked prodi/indikator in the future.
    """

    pass


class EvidenceIndikatorRequest(BaseModel):
    indikator_id: UUID
    target_akreditasi_id: UUID


class EvidenceIndikatorResponse(BaseModel):
    evidence_id: UUID
    indikator_id: UUID
    target_akreditasi_id: UUID

    model_config = ConfigDict(from_attributes=True)
