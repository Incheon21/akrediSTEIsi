"""Section 3 mapper – Kurikulum, Integrasi, Basic Science, Capstone, Penelitian/PkM summaries."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import (
    LkpsKurikulum,
    LkpsIntegrasiPenelitian,
    LkpsMkBasicScience,
    LkpsCapstoneDesign,
    LkpsPenelitianSummary,
    LkpsPkmSummary,
)
from .base import BaseMapper, CHECK

_PENELITIAN_ROW: dict[str, int] = {
    "perguruan_tinggi_mandiri": 9,
    "dalam_negeri":            10,
    "luar_negeri":             11,
}


class Section3Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_kurikulum()
        self._fill_integrasi()
        self._fill_basic_science()
        self._fill_capstone()
        self._fill_penelitian_summary()
        self._fill_pkm_summary()

    def _fill_kurikulum(self) -> None:
        ws = self.wb["3a1"]
        records = (
            self.db.execute(
                select(LkpsKurikulum)
                .where(LkpsKurikulum.submission_id == self.submission.id)
                .order_by(LkpsKurikulum.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 10 + i
            self.safe_write(ws, f"B{row}", rec.semester)
            self.safe_write(ws, f"C{row}", rec.kode_mk)
            self.safe_write(ws, f"D{row}", rec.nama_mk)
            self.safe_write(ws, f"E{row}", rec.kompetensi)
            self.safe_write(ws, f"F{row}", rec.sks_kuliah)
            self.safe_write(ws, f"G{row}", rec.sks_seminar)
            self.safe_write(ws, f"H{row}", rec.sks_praktikum)
            self.safe_write(ws, f"I{row}", rec.konversi_jam)
            self.safe_write(ws, f"J{row}", rec.dokumen_rps)
            self.safe_write(ws, f"K{row}", rec.unit_penyelenggara)

    def _fill_integrasi(self) -> None:
        ws = self.wb["3a3"]
        records = (
            self.db.execute(
                select(LkpsIntegrasiPenelitian)
                .where(LkpsIntegrasiPenelitian.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 13 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.safe_write(ws, f"C{row}", rec.judul_penelitian_pkm)
            self.safe_write(ws, f"D{row}", rec.mata_kuliah)
            self.safe_write(ws, f"E{row}", rec.bentuk_integrasi)
            self.write_check(ws, "F", row, bool(rec.tahun_ts2))
            self.write_check(ws, "G", row, bool(rec.tahun_ts1))
            self.write_check(ws, "H", row, bool(rec.tahun_ts))
            self.safe_write(ws, f"I{row}", rec.kesesuaian_peta_jalan)
            self.safe_write(ws, f"J{row}", rec.bukti_sahih)
            self.safe_write(ws, f"K{row}", rec.kesesuaian_rps)

    def _fill_basic_science(self) -> None:
        ws = self.wb["3a4"]
        records = (
            self.db.execute(
                select(LkpsMkBasicScience)
                .where(LkpsMkBasicScience.submission_id == self.submission.id)
                .order_by(LkpsMkBasicScience.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 10 + i
            self.safe_write(ws, f"B{row}", rec.nama_mk)
            self.safe_write(ws, f"C{row}", rec.semester)
            self.safe_write(ws, f"D{row}", rec.jumlah_sks)

    def _fill_capstone(self) -> None:
        ws = self.wb["3a5"]
        records = (
            self.db.execute(
                select(LkpsCapstoneDesign)
                .where(LkpsCapstoneDesign.submission_id == self.submission.id)
                .order_by(LkpsCapstoneDesign.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 10 + i
            self.safe_write(ws, f"B{row}", rec.nama_mk_pendukung)
            self.safe_write(ws, f"C{row}", rec.sks_pendukung)
            self.safe_write(ws, f"D{row}", rec.nama_mk_capstone)
            self.safe_write(ws, f"E{row}", rec.sks_capstone)
            self.safe_write(ws, f"F{row}", rec.semester)
            self.safe_write(ws, f"G{row}", rec.cakupan_bahasan)

    def _fill_penelitian_summary(self) -> None:
        ws = self.wb["3b"]
        records = (
            self.db.execute(
                select(LkpsPenelitianSummary)
                .where(LkpsPenelitianSummary.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _PENELITIAN_ROW.get(rec.kode_sumber)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.ts2)
            self.safe_write(ws, f"D{row}", rec.ts1)
            self.safe_write(ws, f"E{row}", rec.ts)
            # F = FORMULA (total) — never written

    def _fill_pkm_summary(self) -> None:
        ws = self.wb["3c"]
        records = (
            self.db.execute(
                select(LkpsPkmSummary)
                .where(LkpsPkmSummary.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _PENELITIAN_ROW.get(rec.kode_sumber)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.ts2)
            self.safe_write(ws, f"D{row}", rec.ts1)
            self.safe_write(ws, f"E{row}", rec.ts)
