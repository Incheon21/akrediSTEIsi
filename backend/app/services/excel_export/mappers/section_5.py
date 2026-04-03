"""Section 5 mapper – Prasarana, K3L Dokumen, K3L Fasilitas."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import LkpsPrasarana, LkpsK3lDokumen, LkpsK3lFasilitas
from .base import BaseMapper


class Section5Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_prasarana()
        self._fill_k3l_dokumen()
        self._fill_k3l_fasilitas()

    def _fill_prasarana(self) -> None:
        ws = self.wb["5a"]
        records = (
            self.db.execute(
                select(LkpsPrasarana)
                .where(LkpsPrasarana.submission_id == self.submission.id)
                .order_by(LkpsPrasarana.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 10 + i
            self.safe_write(ws, f"B{row}", rec.nama_prasarana)
            self.safe_write(ws, f"C{row}", rec.jumlah_prasarana)
            self.safe_write(ws, f"D{row}", rec.nama_sarana)
            self.safe_write(ws, f"E{row}", rec.jumlah_standar_minimal)
            self.safe_write(ws, f"F{row}", rec.jumlah_dimiliki)
            self.write_check(ws, "G", row, rec.kepemilikan == "sendiri")
            self.write_check(ws, "H", row, rec.kepemilikan == "sewa")
            self.write_check(ws, "I", row, rec.kondisi == "terawat")
            self.write_check(ws, "J", row, rec.kondisi == "tidak_terawat")
            self.write_check(ws, "K", row, rec.logbook == "ada")
            self.write_check(ws, "L", row, rec.logbook == "tidak_ada")

    def _fill_k3l_dokumen(self) -> None:
        ws = self.wb["5b"]
        records = (
            self.db.execute(
                select(LkpsK3lDokumen)
                .where(LkpsK3lDokumen.submission_id == self.submission.id)
                .order_by(LkpsK3lDokumen.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 15 + i
            self.safe_write(ws, f"B{row}", rec.jenis_dokumen)
            self.safe_write(ws, f"C{row}", rec.jumlah)
            self.safe_write(ws, f"D{row}", rec.riwayat_pengesahan)

    def _fill_k3l_fasilitas(self) -> None:
        ws = self.wb["5c"]
        records = (
            self.db.execute(
                select(LkpsK3lFasilitas)
                .where(LkpsK3lFasilitas.submission_id == self.submission.id)
                .order_by(LkpsK3lFasilitas.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 16 + i
            self.safe_write(ws, f"B{row}", rec.nama_sarana)
            self.safe_write(ws, f"C{row}", rec.fungsi)
            self.safe_write(ws, f"D{row}", rec.jumlah_unit)
            self.write_check(ws, "E", row, rec.kondisi == "terawat")
            self.write_check(ws, "F", row, rec.kondisi == "tidak_terawat")
