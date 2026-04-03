"""Section 7 mapper – SPMI Dokumen (7a) and SPMI Pelaksanaan (7b)."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import LkpsSpmiDokumen, LkpsSpmiPelaksanaan
from .base import BaseMapper

# 7b has 5 fixed rows for PPEPP cycle items
_PPEPP_ROW = {
    "Penetapan":    5,
    "Pelaksanaan":  6,
    "Evaluasi":     7,
    "Pengendalian": 8,
    "Peningkatan":  9,
}


class Section7Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_spmi_dokumen()
        self._fill_spmi_pelaksanaan()

    def _fill_spmi_dokumen(self) -> None:
        ws = self.wb["7a"]
        records = (
            self.db.execute(
                select(LkpsSpmiDokumen)
                .where(LkpsSpmiDokumen.submission_id == self.submission.id)
                .order_by(LkpsSpmiDokumen.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 5 + i
            self.safe_write(ws, f"B{row}", rec.jenis_dokumen)
            self.safe_write(ws, f"C{row}", rec.no_dokumen)
            self.safe_write(ws, f"D{row}", rec.tanggal_dokumen)

    def _fill_spmi_pelaksanaan(self) -> None:
        ws = self.wb["7b"]
        records = (
            self.db.execute(
                select(LkpsSpmiPelaksanaan)
                .where(LkpsSpmiPelaksanaan.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _PPEPP_ROW.get(rec.jenis_pelaksanaan)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.link_dokumen)
            self.safe_write(ws, f"D{row}", rec.link_laporan_audit)
            self.safe_write(ws, f"E{row}", rec.link_laporan_rtm)
            self.safe_write(ws, f"F{row}", rec.link_dokumen_peningkatan)
