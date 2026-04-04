"""Section 4 mapper – Dosen, Tenaga Kependidikan, Beban Kerja, Publikasi, Luaran, dll."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import (
    LkpsDosenProfil,
    LkpsTenagaKependidikan,
    LkpsBebanKerjaDosen,
    LkpsPublikasiIlmiah,
    LkpsLuaranPenelitian,
    LkpsProdukJasa,
    LkpsKinerjaDtps,
    LkpsSitasiDtps,
    LkpsRekognisiDtps,
    LkpsPembimbingLapangan,
)
from .base import BaseMapper, CHECK

# Pendidikan terakhir → column in sheet 4b (C=S3, D=S2, E=S1, F=D4, G=D3, H=D2, I=D1, J=SMA_SMK)
_PENDIDIKAN_COL: dict[str, str] = {
    "S3": "C", "S2": "D", "S1": "E",
    "D4": "F", "D3": "G", "D2": "H", "D1": "I", "SMA_SMK": "J",
}

# Section 4d/4e: kode_publikasi → fixed template row
_PUBLIKASI_ROW_AKADEMIK: dict[str, int] = {
    "jurnal_nasional_tidak_terakreditasi":    7,
    "jurnal_nasional_terakreditasi":          8,
    "jurnal_internasional":                   9,
    "jurnal_internasional_bereputasi":       10,
    "prosiding_nasional":                    11,
    "prosiding_internasional_tidak_terindeks": 12,
    "prosiding_internasional_terindeks":     13,
    # row 14 = FORMULA total
}

_PUBLIKASI_ROW_VOKASI: dict[str, int] = {
    **_PUBLIKASI_ROW_AKADEMIK,
    "pagelaran_wilayah":       14,
    "pagelaran_nasional":      15,
    "pagelaran_internasional": 16,
    # row 17 = FORMULA total
}

# Luaran sheet names by (sumber, jenis_luaran)
_LUARAN_SHEET: dict[tuple[str, str], str] = {
    ("dtps",      "paten"):      "4f-1",
    ("dtps",      "hak_cipta"):  "4f-2",
    ("dtps",      "teknologi"):  "4f-3",
    ("dtps",      "buku"):       "4f-4",
    ("mahasiswa", "paten"):      "6e3-1",
    ("mahasiswa", "hak_cipta"):  "6e3-2",
    ("mahasiswa", "teknologi"):  "6e3-3",
    ("mahasiswa", "buku"):       "6e3-4",
}

# Data start rows for luaran sheets (after category header rows)
_LUARAN_START: dict[str, int] = {
    "4f-1": 7, "4f-2": 7, "4f-3": 16, "4f-4": 7,
    "6e3-1": 12, "6e3-2": 8, "6e3-3": 16, "6e3-4": 8,
}


class Section4Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_dosen_profil()
        self._fill_tendik()
        self._fill_beban_kerja()
        self._fill_publikasi_dtps()
        self._fill_luaran_dtps()
        self._fill_produk_jasa_dtps()
        self._fill_kinerja_dtps()
        self._fill_sitasi_dtps()
        self._fill_rekognisi_dtps()
        self._fill_pembimbing_lapangan()

    def _fill_dosen_profil(self) -> None:
        ws = self.wb["4a"]
        records = (
            self.db.execute(
                select(LkpsDosenProfil)
                .where(LkpsDosenProfil.submission_id == self.submission.id)
                .order_by(LkpsDosenProfil.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 14 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.safe_write(ws, f"C{row}", rec.nidn_nidk)
            self.safe_write(ws, f"D{row}", rec.kategori)
            self.safe_write(ws, f"E{row}", rec.prodi_sarjana)
            self.safe_write(ws, f"F{row}", rec.prodi_magister)
            self.safe_write(ws, f"G{row}", rec.prodi_doktor)
            self.safe_write(ws, f"H{row}", rec.bidang_keahlian)
            self.safe_write(ws, f"I{row}", rec.perusahaan_industri)
            self.safe_write(ws, f"J{row}", rec.kesesuaian_kompetensi)
            self.safe_write(ws, f"K{row}", rec.jabatan_akademik)
            self.safe_write(ws, f"L{row}", rec.no_sertifikat_pendidik)

    def _fill_tendik(self) -> None:
        ws = self.wb["4b"]
        records = (
            self.db.execute(
                select(LkpsTenagaKependidikan)
                .where(LkpsTenagaKependidikan.submission_id == self.submission.id)
                .order_by(LkpsTenagaKependidikan.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 11 + i
            self.safe_write(ws, f"B{row}", rec.nama)
            # Pendidikan terakhir → CHECK in the correct column
            for level, col in _PENDIDIKAN_COL.items():
                self.write_check(ws, col, row, rec.pendidikan_terakhir == level)
            self.safe_write(ws, f"K{row}", rec.sertifikat_kompetensi)
            self.safe_write(ws, f"L{row}", rec.unit_kerja)

    def _fill_beban_kerja(self) -> None:
        ws = self.wb["4c"]
        records = (
            self.db.execute(
                select(LkpsBebanKerjaDosen)
                .where(LkpsBebanKerjaDosen.submission_id == self.submission.id)
                .order_by(LkpsBebanKerjaDosen.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 11 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.write_check(ws, "C", row, bool(rec.dtps))
            self.safe_write(ws, f"D{row}", rec.bk_ps_diakreditasi)
            self.safe_write(ws, f"E{row}", rec.bk_ps_lain_pt)
            self.safe_write(ws, f"F{row}", rec.bk_ps_luar_pt)
            self.safe_write(ws, f"G{row}", rec.bk_penelitian)
            self.safe_write(ws, f"H{row}", rec.bk_pkm)
            self.safe_write(ws, f"I{row}", rec.bk_tugas_tambahan)
            # J=total/tahun, K=total/semester are formulas — never written

    def _fill_publikasi_dtps(self) -> None:
        # Sheet 4d = akademik DTPS
        self._write_publikasi_rows(
            sheet_name="4d",
            row_map=_PUBLIKASI_ROW_AKADEMIK,
            sumber="dtps",
            jenis_program="akademik",
        )
        # Sheet 4e = vokasi DTPS
        self._write_publikasi_rows(
            sheet_name="4e",
            row_map=_PUBLIKASI_ROW_VOKASI,
            sumber="dtps",
            jenis_program="vokasi",
        )

    def _write_publikasi_rows(
        self, sheet_name: str, row_map: dict[str, int],
        sumber: str, jenis_program: str,
    ) -> None:
        ws = self.wb[sheet_name]
        records = (
            self.db.execute(
                select(LkpsPublikasiIlmiah)
                .where(
                    LkpsPublikasiIlmiah.submission_id == self.submission.id,
                    LkpsPublikasiIlmiah.sumber == sumber,
                    LkpsPublikasiIlmiah.jenis_program == jenis_program,
                )
            )
            .scalars().all()
        )
        for rec in records:
            row = row_map.get(rec.kode_publikasi)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.ts2)
            self.safe_write(ws, f"D{row}", rec.ts1)
            self.safe_write(ws, f"E{row}", rec.ts)
            # F = FORMULA (total) — never written

    def _fill_luaran_dtps(self) -> None:
        for jenis in ("paten", "hak_cipta", "teknologi", "buku"):
            sheet_name = _LUARAN_SHEET.get(("dtps", jenis))
            if not sheet_name:
                continue
            self._write_luaran_rows(sheet_name=sheet_name, sumber="dtps", jenis=jenis)

    def _write_luaran_rows(self, sheet_name: str, sumber: str, jenis: str) -> None:
        ws = self.wb[sheet_name]
        start = _LUARAN_START[sheet_name]
        records = (
            self.db.execute(
                select(LkpsLuaranPenelitian)
                .where(
                    LkpsLuaranPenelitian.submission_id == self.submission.id,
                    LkpsLuaranPenelitian.sumber == sumber,
                    LkpsLuaranPenelitian.jenis_luaran == jenis,
                )
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = start + i
            self.safe_write(ws, f"B{row}", rec.judul)
            self.safe_write(ws, f"C{row}", rec.tanggal)
            if jenis == "paten":
                self.safe_write(ws, f"D{row}", rec.nomor_paten)
                if sumber == "mahasiswa":
                    self.safe_write(ws, f"D{row}", rec.status_mahasiswa)
                    self.safe_write(ws, f"E{row}", rec.nomor_paten)
            elif jenis == "hak_cipta":
                self.safe_write(ws, f"D{row}", rec.nomor_hki)
            elif jenis == "teknologi":
                self.safe_write(ws, f"D{row}", rec.status_tkt)
                self.safe_write(ws, f"E{row}", rec.nomor_sertifikat_tkt)
            elif jenis == "buku":
                self.safe_write(ws, f"D{row}", rec.nomor_isbn)

    def _fill_produk_jasa_dtps(self) -> None:
        ws = self.wb["4g"]
        records = (
            self.db.execute(
                select(LkpsProdukJasa)
                .where(
                    LkpsProdukJasa.submission_id == self.submission.id,
                    LkpsProdukJasa.sumber == "dtps",
                )
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 6 + i
            self.safe_write(ws, f"B{row}", rec.nama_pembuat)
            self.safe_write(ws, f"C{row}", rec.nama_produk_jasa)
            self.safe_write(ws, f"D{row}", rec.deskripsi)
            self.safe_write(ws, f"E{row}", rec.bukti)

    def _fill_kinerja_dtps(self) -> None:
        ws = self.wb["4h"]
        records = (
            self.db.execute(
                select(LkpsKinerjaDtps)
                .where(LkpsKinerjaDtps.submission_id == self.submission.id)
                .order_by(LkpsKinerjaDtps.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 16 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.safe_write(ws, f"C{row}", rec.ts2)
            self.safe_write(ws, f"D{row}", rec.ts1)
            self.safe_write(ws, f"E{row}", rec.ts)
            self.safe_write(ws, f"F{row}", rec.keterangan)
            # G = FORMULA total — never written

    def _fill_sitasi_dtps(self) -> None:
        ws = self.wb["4i"]
        records = (
            self.db.execute(
                select(LkpsSitasiDtps)
                .where(LkpsSitasiDtps.submission_id == self.submission.id)
                .order_by(LkpsSitasiDtps.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 6 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.safe_write(ws, f"C{row}", rec.judul_artikel)
            self.safe_write(ws, f"D{row}", rec.jumlah_sitasi)

    def _fill_rekognisi_dtps(self) -> None:
        ws = self.wb["4j"]
        records = (
            self.db.execute(
                select(LkpsRekognisiDtps)
                .where(LkpsRekognisiDtps.submission_id == self.submission.id)
                .order_by(LkpsRekognisiDtps.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 12 + i
            self.safe_write(ws, f"B{row}", rec.nama_dosen)
            self.safe_write(ws, f"C{row}", rec.bidang_keahlian)
            self.safe_write(ws, f"D{row}", rec.rekognisi)
            self.safe_write(ws, f"E{row}", rec.bukti_pendukung)
            self.write_tingkat_check(ws, row, rec.tingkat, "H", "G", "F")
            self.safe_write(ws, f"I{row}", rec.tahun)

    def _fill_pembimbing_lapangan(self) -> None:
        ws = self.wb["4k"]
        records = (
            self.db.execute(
                select(LkpsPembimbingLapangan)
                .where(LkpsPembimbingLapangan.submission_id == self.submission.id)
                .order_by(LkpsPembimbingLapangan.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 6 + i
            self.safe_write(ws, f"B{row}", rec.nama)
            self.safe_write(ws, f"C{row}", rec.industri)
            self.safe_write(ws, f"D{row}", rec.bidang_keinsinyuran)
            self.safe_write(ws, f"E{row}", rec.pengalaman_kerja_tahun)
            self.safe_write(ws, f"F{row}", rec.pendidikan_tinggi)
            self.write_check(ws, "G", row, rec.kategori_sip == "IPM")
            self.write_check(ws, "H", row, rec.kategori_sip == "IPU")
            self.safe_write(ws, f"I{row}", rec.nomor_sip)
            self.safe_write(ws, f"J{row}", rec.tanggal_berakhir_sip)
            self.safe_write(ws, f"K{row}", rec.jumlah_bimbingan_3tahun)
