from typing import Dict, List

from pydantic import BaseModel, Field


class IndikatorInput(BaseModel):
    kode_indikator: str
    nilai_input: float


class SimulasiRequest(BaseModel):
    lembaga: str = Field(..., description="TEKNIK atau INFOKOM")
    jenjang: str = Field(..., description="SARJANA, MAGISTER, atau DOKTOR")
    data_input: List[IndikatorInput]
    data_proses: List[IndikatorInput]
    data_output: List[IndikatorInput]


class SimulasiResponse(BaseModel):
    nilai_akhir: float
    status_prediksi: str
    keterangan: str
    breakdown_skor: Dict[str, float]
