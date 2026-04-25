from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgramStudiBase(BaseModel):
    kode: str
    nama: str
    jenjang: str
    fakultas: str | None = None
    perguruan_tinggi: str | None = None
    akreditasi: str | None = None
    no_sk_ban_pt: str | None = None
    tanggal_akreditasi: datetime | None = None
    tanggal_kadaluarsa: datetime | None = None
    status: str | None = "aktif"
    alamat: str | None = None
    kota: str | None = None
    kode_pos: str | None = None
    nomor_telepon: str | None = None
    email: str | None = None
    website: str | None = None
    no_sk_pendirian_pt: str | None = None
    tanggal_sk_pendirian_pt: datetime | None = None
    pejabat_sk_pendirian_pt: str | None = None
    no_sk_pembukaan_ps: str | None = None
    tanggal_sk_pembukaan_ps: datetime | None = None
    pejabat_sk_pembukaan_ps: str | None = None
    tahun_pertama_menerima_mahasiswa: int | None = None


class ProgramStudiCreate(ProgramStudiBase):
    pass


class ProgramStudiUpdate(BaseModel):
    kode: str | None = None
    nama: str | None = None
    jenjang: str | None = None
    fakultas: str | None = None
    perguruan_tinggi: str | None = None
    akreditasi: str | None = None
    no_sk_ban_pt: str | None = None
    tanggal_akreditasi: datetime | None = None
    tanggal_kadaluarsa: datetime | None = None
    status: str | None = None
    alamat: str | None = None
    kota: str | None = None
    kode_pos: str | None = None
    nomor_telepon: str | None = None
    email: str | None = None
    website: str | None = None
    no_sk_pendirian_pt: str | None = None
    tanggal_sk_pendirian_pt: datetime | None = None
    pejabat_sk_pendirian_pt: str | None = None
    no_sk_pembukaan_ps: str | None = None
    tanggal_sk_pembukaan_ps: datetime | None = None
    pejabat_sk_pembukaan_ps: str | None = None
    tahun_pertama_menerima_mahasiswa: int | None = None


class ProgramStudiResponse(ProgramStudiBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
