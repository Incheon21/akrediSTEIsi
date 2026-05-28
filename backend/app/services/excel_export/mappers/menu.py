"""Menu and Daftar Tabel sheet mappers.

MenuMapper fills program studi identity fields. Must run first because
Menu!S73 is the master TS date referenced by kerjasama status formulas.

DaftarTabelMapper rewrites the √ marks in Daftar Tabel to reflect only the
sheets that apply to the submission's jenjang.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select

from app.models.lkps import LkpsMahasiswaAktif, LkpsPppiDisiplin
from .base import BaseMapper, CHECK, _SHEET_JENJANG

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
        self.safe_write(ws, "H39", ps.alamat)                 # Alamat
        self.safe_write(ws, "H43", ps.kota)                   # Kota
        self.safe_write(ws, "U43", ps.kode_pos)               # Kode Pos
        self.safe_write(ws, "H45", ps.nomor_telepon)          # Nomor Telepon
        self.safe_write(ws, "H47", ps.email)                  # Email
        self.safe_write(ws, "H49", ps.website)                # Website
        self.safe_write(ws, "H51", ps.no_sk_pendirian_pt)     # No SK Pendirian PT
        if ps.tanggal_sk_pendirian_pt:
            self.safe_write(ws, "H53", ps.tanggal_sk_pendirian_pt.date())
        self.safe_write(ws, "H55", ps.pejabat_sk_pendirian_pt)  # Pejabat SK Pendirian PT
        self.safe_write(ws, "H57", ps.no_sk_pembukaan_ps)     # No SK Pembukaan PS
        if ps.tanggal_sk_pembukaan_ps:
            self.safe_write(ws, "H59", ps.tanggal_sk_pembukaan_ps.date())
        self.safe_write(ws, "H61", ps.pejabat_sk_pembukaan_ps)  # Pejabat SK Pembukaan PS
        self.safe_write(ws, "H63", ps.tahun_pertama_menerima_mahasiswa)  # Tahun pertama
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


# Daftar Tabel: sheet_name → row number (rows 4-55 in the template)
_DAFTAR_ROW: dict[str, int] = {
    "PS": 4, "PSPPI": 5, "1": 6, "2a1": 7, "2a2": 8, "2a3": 9,
    "2b": 10, "3a1": 11, "3a2": 12, "3a3": 13, "3a4": 14, "3a5": 15,
    "3b": 16, "3c": 17, "4a": 18, "4b": 19, "4c": 20, "4d": 21,
    "4e": 22, "4f-1": 23, "4f-2": 24, "4f-3": 25, "4f-4": 26,
    "4g": 27, "4h": 28, "4i": 29, "4j": 30, "4k": 31, "5a": 32,
    "5b": 33, "5c": 34, "6a": 35, "6b": 36, "6c1": 37, "6c2": 38,
    "6d": 39, "6e1": 40, "6e2": 41, "6e3-1": 42, "6e3-2": 43,
    "6e3-3": 44, "6e3-4": 45, "6e4": 46, "6f1": 47, "6f2": 48,
    "6g1": 49, "6g2": 50, "6h1": 51, "6h2": 52, "6i": 53,
    "7a": 54, "7b": 55,
}

# Daftar Tabel: jenjang code → column letter
_DAFTAR_COL: dict[str, str] = {
    "D1": "E", "D2": "F", "D3": "G",
    "S1": "H", "S1Tr": "I",
    "S2": "J", "S2Tr": "K",
    "S3": "L", "S3Tr": "M",
    "PPI": "N",
}


class DaftarTabelMapper(BaseMapper):
    """Rewrites Daftar Tabel √ marks to reflect the submission's jenjang only."""

    def fill(self) -> None:
        ws = self.wb["Daftar Tabel"]
        jenjang = self.submission.program_studi.jenjang
        col = _DAFTAR_COL.get(jenjang)
        if col is None:
            return  # unknown jenjang — leave template as-is

        for sheet_name, row in _DAFTAR_ROW.items():
            allowed = _SHEET_JENJANG.get(sheet_name)
            applies = allowed is not None and jenjang in allowed
            self.safe_write(ws, f"{col}{row}", CHECK if applies else None)


class ProgramStudiSheetMapper(BaseMapper):
    """Fills static identity tabs whose data comes from ProgramStudi/LKPS data."""

    def fill(self) -> None:
        self._fill_ps_sheet()
        self._fill_pppi_sheet()

    def _fill_ps_sheet(self) -> None:
        if not self.sheet_applies("PS"):
            return
        ws = self.wb["PS"]
        ps = self.submission.program_studi

        mahasiswa_aktif = (
            self.db.execute(
                select(LkpsMahasiswaAktif)
                .where(
                    LkpsMahasiswaAktif.submission_id == self.submission.id,
                    LkpsMahasiswaAktif.prodi_diakreditasi.is_(True),
                )
                .order_by(LkpsMahasiswaAktif.no)
            )
            .scalars()
            .first()
        )

        sk_parts = [part for part in (ps.no_sk_ban_pt, _date_value(ps.tanggal_akreditasi)) if part]
        self.safe_write(ws, "B17", ps.jenjang)
        self.safe_write(ws, "C17", ps.nama)
        self.safe_write(ws, "D17", ps.akreditasi)
        self.safe_write(ws, "E17", " / ".join(str(part) for part in sk_parts) if sk_parts else None)
        self.safe_write(ws, "F17", _date_value(ps.tanggal_kadaluarsa))
        self.safe_write(ws, "G17", mahasiswa_aktif.aktif_ts if mahasiswa_aktif else None)

    def _fill_pppi_sheet(self) -> None:
        if not self.sheet_applies("PSPPI"):
            return
        ws = self.wb["PSPPI"]
        records = (
            self.db.execute(
                select(LkpsPppiDisiplin)
                .where(LkpsPppiDisiplin.submission_id == self.submission.id)
                .order_by(LkpsPppiDisiplin.no)
            )
            .scalars()
            .all()
        )

        row_by_discipline = {
            "Kebumian dan Energi": 17,
            "Rekayasa Sipil dan Lingkungan Terbangun": 18,
            "Industri": 19,
            "Konservasi dan Pengelolaan Sumber Daya Alam": 20,
            "Pertanian dan Hasil Pertanian": 21,
            "Teknologi Kelautan dan Perkapalan": 22,
            "Aeronotika dan Astronotika": 23,
        }
        for rec in records:
            row = row_by_discipline.get(rec.disiplin)
            if row is None:
                continue
            self.write_check(ws, "C", row, bool(rec.diselenggarakan))
            self.write_check(ws, "D", row, not bool(rec.diselenggarakan))


def _date_value(value):
    if value is None:
        return None
    if hasattr(value, "date"):
        return value.date()
    return value
