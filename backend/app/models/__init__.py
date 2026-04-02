from app.models.program_studi import ProgramStudi
from app.models.role import Role
from app.models.user import User
from app.models.kriteria import Kriteria
from app.models.indikator import Indikator
from app.models.target_akreditasi import TargetAkreditasi
from app.models.evidence import Evidence, EvidenceProdi, EvidenceIndikator
from app.models.data_lkps import DataLKPS
from app.models.narasi_led import NarasiLED

__all__ = [
    "ProgramStudi",
    "Role",
    "User",
    "Kriteria",
    "Indikator",
    "TargetAkreditasi",
    "Evidence",
    "EvidenceProdi",
    "EvidenceIndikator",
    "DataLKPS",
    "NarasiLED",
]
