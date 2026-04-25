"""Section 2 mapper – Kerjasama (2a1/2a2/2a3) and Penggunaan Dana (2b)."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import LkpsKerjasama, LkpsPenggunaanDana
from .base import BaseMapper

# Data rows start at different rows per sheet: 2a1→13, 2a2/2a3→12
_KERJASAMA_DATA_START = {
    "2a1": 13,
    "2a2": 12,
    "2a3": 12,
}

# jenis → sheet name
_JENIS_SHEET = {
    "pendidikan": "2a1",
    "penelitian":  "2a2",
    "pkm":         "2a3",
}

# Fixed row map for sheet 2b.
# Formula rows (14, 17, 18) are intentionally absent — safe_write would skip
# them anyway, but we never query for those kode values either.
_DANA_ROW: dict[str, int] = {
    "biaya_dosen":               7,
    "biaya_tendik":              8,
    "biaya_op_pembelajaran":     9,
    "biaya_op_tidak_langsung":  10,
    "biaya_praktik_ppi":        11,
    "biaya_investasi":          12,
    "biaya_kemahasiswaan":      13,
    "biaya_penelitian":         15,
    "biaya_pkm":                16,
}


class Section2Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_kerjasama()
        self._fill_dana()

    # ------------------------------------------------------------------
    # 2a1 / 2a2 / 2a3 – Kerjasama
    # ------------------------------------------------------------------

    def _fill_kerjasama(self) -> None:
        for jenis, sheet_name in _JENIS_SHEET.items():
            ws = self.wb[sheet_name]
            records = (
                self.db.execute(
                    select(LkpsKerjasama)
                    .where(
                        LkpsKerjasama.submission_id == self.submission.id,
                        LkpsKerjasama.jenis == jenis,
                    )
                    .order_by(LkpsKerjasama.lembaga_mitra)
                )
                .scalars()
                .all()
            )
            for i, rec in enumerate(records):
                row = _KERJASAMA_DATA_START[sheet_name] + i
                self.safe_write(ws, f"B{row}", rec.lembaga_mitra)
                # Tingkat → write CHECK to exactly one of cols C/D/E
                self.write_tingkat_check(ws, row, rec.tingkat, "C", "D", "E")
                self.safe_write(ws, f"F{row}", rec.judul_kegiatan)
                self.safe_write(ws, f"G{row}", rec.manfaat)
                self.safe_write(ws, f"H{row}", rec.tanggal_awal)   # date; J=durasi formula uses this
                self.safe_write(ws, f"I{row}", rec.tanggal_akhir)  # date; K=status formula uses this
                self.safe_write(ws, f"L{row}", rec.bukti_kerjasama)
                # Columns J (durasi) and K (status) are formulas — never written

    # ------------------------------------------------------------------
    # 2b – Penggunaan Dana
    # ------------------------------------------------------------------

    def _fill_dana(self) -> None:
        ws = self.wb["2b"]
        records = (
            self.db.execute(
                select(LkpsPenggunaanDana)
                .where(LkpsPenggunaanDana.submission_id == self.submission.id)
            )
            .scalars()
            .all()
        )
        for rec in records:
            row = _DANA_ROW.get(rec.kode)
            if row is None:
                continue
            # UPPS columns (C=TS-2, D=TS-1, E=TS); F=avg is formula
            self.safe_write(ws, f"C{row}", rec.upps_ts2)
            self.safe_write(ws, f"D{row}", rec.upps_ts1)
            self.safe_write(ws, f"E{row}", rec.upps_ts)
            # PS columns (G=TS-2, H=TS-1, I=TS); J=avg is formula
            self.safe_write(ws, f"G{row}", rec.ps_ts2)
            self.safe_write(ws, f"H{row}", rec.ps_ts1)
            self.safe_write(ws, f"I{row}", rec.ps_ts)
