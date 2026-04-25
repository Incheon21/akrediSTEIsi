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
    lkps_progress: int = 0
    led_progress: int = 0
    has_lkps: bool
    lkps_available: bool
    has_led: bool
    led_available: bool
    has_evidence: bool


class DashboardProdiResponse(BaseModel):
    program_studi_profile: ProfilProdiSchema
    target_akreditasi_id: str
    lkps_submission_id: str
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

class FakultasSummarySchema(BaseModel):
    total_prodi: int
    prodi_green: int
    prodi_yellow: int
    prodi_red: int
    avg_lkps_percent: float
    avg_led_percent: float
    avg_simulation_score: float


class ProdiSummarySchema(BaseModel):
    id: str
    name: str
    degree: str
    accreditation_status: str
    accreditation_year: int
    lkps_percent: int
    led_percent: int
    evidence_percent: int
    simulation_score: float
    target_score: float
    readiness_status: str
    is_active: bool
    days_remaining: Optional[int] = None


class DashboardMultiProdiResponse(BaseModel):
    fakultas_summary: FakultasSummarySchema
    prodi_list: List[ProdiSummarySchema]
    current_year: int
    available_years: List[int]
