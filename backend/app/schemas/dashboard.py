from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ProfilProdiSchema(BaseModel):
    name: str
    degree: str
    last_accreditation_status: str
    last_accreditation_year: int
    is_active_accreditation: bool


class KriteriaRowSchema(BaseModel):
    id: str
    name: str
    status: str
    status_label: str
    progress: int
    has_lkps: bool
    lkps_available: bool
    has_led: bool
    led_available: bool
    has_evidence: bool


class DashboardProdiResponse(BaseModel):
    program_studi_profile: ProfilProdiSchema
    target_akreditasi_id: str
    current_year: int
    available_years: List[int]
    criteria_list: List[KriteriaRowSchema]
    recommendation_messages: List[str]
    early_warnings: List[str]
    score_value: float
    target_score: float
    deadline: Optional[str] = None
    days_remaining: Optional[int] = None

    # Overview progress bars
    lkps_percent: int
    led_percent: int
    evidence_percent: int


class DashboardMultiProdiResponse(BaseModel):
    data_prodi: List[DashboardProdiResponse]
