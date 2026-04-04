"""Menu sheet mapper.

Fills the template's Menu sheet with program studi identity fields.
Menu!S73 is the MASTER TS date — all kerjasama status formulas in sheets
2a1/2a2/2a3 reference it.  This mapper MUST run before all others.
"""

from __future__ import annotations

from datetime import date

from .base import BaseMapper, CHECK

# Jenjang string → row in Menu where the checkbox "√" is placed (col G)
_JENJANG_ROW: dict[str, int] = {
    "D1": 13, "D2": 14, "D3": 15,
    "S1": 16, "S1Tr": 17,
    "S2": 18, "S2Tr": 19,
    "S3": 20, "S3Tr": 21,
}

# Akreditasi peringkat → row for checkbox (col G)
_AKREDITASI_ROW: dict[str, int] = {
    "Unggul": 25, "A": 26, "Baik Sekali": 27,
    "B": 28, "Baik": 29, "C": 30, "Minimum": 31,
}


class MenuMapper(BaseMapper):
    def fill(self) -> None:
        ws = self.wb["Menu"]
        ps = self.submission.program_studi

        # Identity cells (merged, write to the first cell of each merged region)
        self.safe_write(ws, "H7",  ps.perguruan_tinggi)       # Perguruan Tinggi
        self.safe_write(ws, "H9",  ps.fakultas)               # Unit Pengelola PS
        self.safe_write(ws, "H23", ps.nama)                   # Nama Program Studi
        self.safe_write(ws, "H65", ps.akreditasi)             # Peringkat Akreditasi
        self.safe_write(ws, "H67", ps.no_sk_ban_pt)           # Nomor SK BAN-PT

        # Jenis Program checkbox (col G, rows 13-21)
        jenjang = ps.jenjang
        for jj, row in _JENJANG_ROW.items():
            self.safe_write(ws, f"G{row}", CHECK if jj == jenjang else None)

        # Nama Pengusul & tanggal pengajuan
        self.safe_write(ws, "S69", self.submission.nama_pengusul)
        if self.submission.tanggal_pengajuan:
            self.safe_write(ws, "S71", self.submission.tanggal_pengajuan)

        # TS date → Menu!S73 (drives all K-column "Status Kerjasama" formulas)
        ts_date = date(self.submission.tahun_ts, 8, 31)
        self.safe_write(ws, "S73", ts_date)
