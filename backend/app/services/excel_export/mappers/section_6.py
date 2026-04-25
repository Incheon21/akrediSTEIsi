"""Section 6 mapper – Mahasiswa, Lulusan, Prestasi, Publikasi Mahasiswa, dll."""

from __future__ import annotations

from sqlalchemy import select

from app.models.lkps import (
    LkpsMahasiswaAktif,
    LkpsIpkLulusan,
    LkpsPrestasiMahasiswa,
    LkpsMasaStudi,
    LkpsPublikasiIlmiah,
    LkpsLuaranPenelitian,
    LkpsProdukJasa,
    LkpsWaktuTunggu,
    LkpsKesesuaianKerja,
    LkpsTempatKerja,
    LkpsKepuasanPengguna,
    LkpsPenelitianMahasiswa,
)
from .base import BaseMapper

# IPK rows: periode → row number in sheet 6b
_IPK_ROW = {"TS-2": 6, "TS-1": 7, "TS": 8}

# 6f1: waktu tunggu per-jenis_program section first data row
_WT_SECTION_START: dict[str, int] = {
    "D1":  7, "D2": 15, "D3": 23,
    "S1": 31, "S1Tr": 39, "PPI": 47,
}
_WT_TAHUN_OFFSET = {"TS-2": 0, "TS-1": 1}

# Kesesuaian kerja (6f2) & tempat kerja (6g1) — single shared section, rows 7-8
_LULUSAN_ROW = {"TS-2": 7, "TS-1": 8}

# Kepuasan pengguna fixed-row items (rows 7-13 standard items)
# These rows have pre-labeled jenis_kemampuan; only score columns are written.
_KEPUASAN_ROW = {
    "Etika":                              7,
    "Keahlian pada bidang ilmu (kompetensi utama)": 8,
    "Kemampuan berbahasa asing":          9,
    "Penggunaan teknologi informasi":    10,
    "Kemampuan berkomunikasi":           11,
    "Kerjasama tim":                     12,
    "Pengembangan diri":                 13,
}

# 6e1/6e2 – publikasi mahasiswa (same row map as 4d/4e)
_PUBLIKASI_ROW_AKADEMIK: dict[str, int] = {
    "jurnal_nasional_tidak_terakreditasi":    7,
    "jurnal_nasional_terakreditasi":          8,
    "jurnal_internasional":                   9,
    "jurnal_internasional_bereputasi":       10,
    "prosiding_nasional":                    11,
    "prosiding_internasional_tidak_terindeks": 12,
    "prosiding_internasional_terindeks":     13,
}
_PUBLIKASI_ROW_VOKASI: dict[str, int] = {
    **_PUBLIKASI_ROW_AKADEMIK,
    "pagelaran_wilayah":       14,
    "pagelaran_nasional":      15,
    "pagelaran_internasional": 16,
}

_LUARAN_START: dict[str, int] = {
    "6e3-1": 12, "6e3-2": 8, "6e3-3": 18, "6e3-4": 8,
}


# 6d: per-jenis_program row offsets (first data row) and year labels in order
_MASA_STUDI_SECTIONS: dict[str, tuple[int, list[str], list[str]]] = {
    # jenis_program: (first_data_row, tahun_masuk_labels, data_cols)
    "D1":   (7,  ["TS-1", "TS"],                              ["B", "C", "D", "E"]),
    "D2":   (14, ["TS-3", "TS-2", "TS-1", "TS"],             ["B", "C", "D", "E"]),
    "D3":   (23, ["TS-5", "TS-4", "TS-3", "TS-2", "TS-1", "TS"], ["B", "C", "D", "E"]),
    "S1":   (34, ["TS-7", "TS-6", "TS-5", "TS-4", "TS-3", "TS-2", "TS-1", "TS"],
                 ["B", "C", "D", "E", "F"]),
    "S1Tr": (34, ["TS-7", "TS-6", "TS-5", "TS-4", "TS-3", "TS-2", "TS-1", "TS"],
                 ["B", "C", "D", "E", "F"]),
    "S2":   (47, ["TS-3", "TS-2", "TS-1", "TS"],             ["B", "C", "D", "E"]),
    "S2Tr": (47, ["TS-3", "TS-2", "TS-1", "TS"],             ["B", "C", "D", "E"]),
    "S3":   (56, ["TS-5", "TS-4", "TS-3", "TS-2", "TS-1", "TS"], ["B", "C", "D", "E"]),
    "S3Tr": (56, ["TS-5", "TS-4", "TS-3", "TS-2", "TS-1", "TS"], ["B", "C", "D", "E"]),
    "PPI":  (67, ["TS-2", "TS-1", "TS"],                     ["B", "C", "D", "E"]),
}


class Section6Mapper(BaseMapper):
    def fill(self) -> None:
        self._fill_mahasiswa_aktif()
        self._fill_ipk()
        self._fill_prestasi()
        self._fill_masa_studi()
        self._fill_publikasi_mahasiswa()
        self._fill_luaran_mahasiswa()
        self._fill_produk_jasa_mahasiswa()
        self._fill_waktu_tunggu()
        self._fill_kesesuaian_kerja()
        self._fill_tempat_kerja()
        self._fill_kepuasan_pengguna()
        self._fill_penelitian_mahasiswa()

    def _fill_mahasiswa_aktif(self) -> None:
        ws = self.wb["6a"]
        records = (
            self.db.execute(
                select(LkpsMahasiswaAktif)
                .where(LkpsMahasiswaAktif.submission_id == self.submission.id)
                .order_by(LkpsMahasiswaAktif.no)
            )
            .scalars().all()
        )
        for i, rec in enumerate(records):
            row = 7 + i
            self.safe_write(ws, f"B{row}", rec.program_studi_nama)
            self.safe_write(ws, f"C{row}", "√" if rec.prodi_diakreditasi else None)
            self.safe_write(ws, f"D{row}", rec.aktif_ts2)
            self.safe_write(ws, f"E{row}", rec.aktif_ts1)
            self.safe_write(ws, f"F{row}", rec.aktif_ts)
            self.safe_write(ws, f"G{row}", rec.asing_fulltime_ts2)
            self.safe_write(ws, f"H{row}", rec.asing_fulltime_ts1)
            self.safe_write(ws, f"I{row}", rec.asing_fulltime_ts)
            self.safe_write(ws, f"J{row}", rec.asing_parttime_ts2)
            self.safe_write(ws, f"K{row}", rec.asing_parttime_ts1)
            self.safe_write(ws, f"L{row}", rec.asing_parttime_ts)

    def _fill_ipk(self) -> None:
        ws = self.wb["6b"]
        records = (
            self.db.execute(
                select(LkpsIpkLulusan)
                .where(LkpsIpkLulusan.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _IPK_ROW.get(rec.periode)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.jumlah_lulusan)
            self.safe_write(ws, f"D{row}", rec.ipk_min)
            self.safe_write(ws, f"E{row}", rec.ipk_rata)
            self.safe_write(ws, f"F{row}", rec.ipk_maks)

    def _fill_prestasi(self) -> None:
        # 6c1 – akademik, 6c2 – non-akademik
        for jenis, sheet_name, start_row in [
            ("akademik",     "6c1", 10),
            ("non_akademik", "6c2", 11),
        ]:
            ws = self.wb[sheet_name]
            records = (
                self.db.execute(
                    select(LkpsPrestasiMahasiswa)
                    .where(
                        LkpsPrestasiMahasiswa.submission_id == self.submission.id,
                        LkpsPrestasiMahasiswa.jenis == jenis,
                    )
                    .order_by(LkpsPrestasiMahasiswa.no)
                )
                .scalars().all()
            )
            for i, rec in enumerate(records):
                row = start_row + i
                self.safe_write(ws, f"B{row}", rec.nama_kegiatan)
                self.safe_write(ws, f"C{row}", rec.waktu_perolehan)
                self.write_tingkat_check(ws, row, rec.tingkat, "F", "E", "D")
                self.safe_write(ws, f"G{row}", rec.prestasi_dicapai)

    def _fill_masa_studi(self) -> None:
        ws = self.wb["6d"]
        records = (
            self.db.execute(
                select(LkpsMasaStudi)
                .where(LkpsMasaStudi.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            section = _MASA_STUDI_SECTIONS.get(rec.jenis_program)
            if section is None:
                continue
            first_row, tahun_labels, cols = section
            try:
                offset = tahun_labels.index(rec.tahun_masuk)
            except ValueError:
                continue
            row = first_row + offset
            self.safe_write(ws, f"B{row}", rec.jumlah_masuk)
            self.safe_write(ws, f"C{row}", rec.jumlah_lulus_tepat_waktu)
            self.safe_write(ws, f"D{row}", rec.jumlah_lulus_terlambat)
            self.safe_write(ws, f"E{row}", rec.jumlah_tidak_lulus)
            # S1/S1Tr has an extra column F for the widest MS bucket — already 5 cols in that section

    def _fill_publikasi_mahasiswa(self) -> None:
        if self.sheet_applies("6e1"):
            self._write_pub_rows("6e1", _PUBLIKASI_ROW_AKADEMIK, "mahasiswa", "akademik")
        if self.sheet_applies("6e2"):
            self._write_pub_rows("6e2", _PUBLIKASI_ROW_VOKASI,   "mahasiswa", "vokasi")

    def _write_pub_rows(
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

    def _fill_luaran_mahasiswa(self) -> None:
        _sheet_map = {
            "paten": "6e3-1", "hak_cipta": "6e3-2",
            "teknologi": "6e3-3", "buku": "6e3-4",
        }
        for jenis, sheet_name in _sheet_map.items():
            ws = self.wb[sheet_name]
            start = _LUARAN_START[sheet_name]
            records = (
                self.db.execute(
                    select(LkpsLuaranPenelitian)
                    .where(
                        LkpsLuaranPenelitian.submission_id == self.submission.id,
                        LkpsLuaranPenelitian.sumber == "mahasiswa",
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
                    self.safe_write(ws, f"D{row}", rec.status_mahasiswa)
                    self.safe_write(ws, f"E{row}", rec.nomor_paten)
                elif jenis == "hak_cipta":
                    self.safe_write(ws, f"D{row}", rec.nomor_hki)
                elif jenis == "teknologi":
                    self.safe_write(ws, f"D{row}", rec.status_tkt)
                    self.safe_write(ws, f"E{row}", rec.nomor_sertifikat_tkt)
                elif jenis == "buku":
                    self.safe_write(ws, f"D{row}", rec.nomor_isbn)

    def _fill_produk_jasa_mahasiswa(self) -> None:
        if not self.sheet_applies("6e4"):
            return
        ws = self.wb["6e4"]
        records = (
            self.db.execute(
                select(LkpsProdukJasa)
                .where(
                    LkpsProdukJasa.submission_id == self.submission.id,
                    LkpsProdukJasa.sumber == "mahasiswa",
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

    def _fill_waktu_tunggu(self) -> None:
        ws = self.wb["6f1"]
        records = (
            self.db.execute(
                select(LkpsWaktuTunggu)
                .where(LkpsWaktuTunggu.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            section_start = _WT_SECTION_START.get(rec.jenis_program)
            offset = _WT_TAHUN_OFFSET.get(rec.tahun_lulus)
            if section_start is None or offset is None:
                continue
            row = section_start + offset
            self.safe_write(ws, f"B{row}", rec.jumlah_lulusan)
            self.safe_write(ws, f"C{row}", rec.jumlah_terlacak)
            self.safe_write(ws, f"D{row}", rec.jumlah_dipesan_sebelum_lulus)
            self.safe_write(ws, f"E{row}", rec.wt_lt_3bulan)
            self.safe_write(ws, f"F{row}", rec.wt_3_6bulan)
            self.safe_write(ws, f"G{row}", rec.wt_gt_6bulan)

    def _fill_kesesuaian_kerja(self) -> None:
        ws = self.wb["6f2"]
        records = (
            self.db.execute(
                select(LkpsKesesuaianKerja)
                .where(LkpsKesesuaianKerja.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _LULUSAN_ROW.get(rec.tahun_lulus)
            if row is None:
                continue
            self.safe_write(ws, f"B{row}", rec.jumlah_lulusan)
            self.safe_write(ws, f"C{row}", rec.jumlah_terlacak)
            self.safe_write(ws, f"D{row}", rec.kesesuaian_rendah)
            self.safe_write(ws, f"E{row}", rec.kesesuaian_sedang)
            self.safe_write(ws, f"F{row}", rec.kesesuaian_tinggi)

    def _fill_tempat_kerja(self) -> None:
        ws = self.wb["6g1"]
        records = (
            self.db.execute(
                select(LkpsTempatKerja)
                .where(LkpsTempatKerja.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            row = _LULUSAN_ROW.get(rec.tahun_lulus)
            if row is None:
                continue
            self.safe_write(ws, f"B{row}", rec.jumlah_lulusan)
            self.safe_write(ws, f"C{row}", rec.jumlah_pengguna_tanggapan)
            self.safe_write(ws, f"D{row}", rec.jumlah_terlacak)
            self.safe_write(ws, f"E{row}", rec.bekerja_lokal)
            self.safe_write(ws, f"F{row}", rec.bekerja_nasional)
            self.safe_write(ws, f"G{row}", rec.bekerja_multinasional)

    def _fill_kepuasan_pengguna(self) -> None:
        ws = self.wb["6g2"]
        records = (
            self.db.execute(
                select(LkpsKepuasanPengguna)
                .where(LkpsKepuasanPengguna.submission_id == self.submission.id)
            )
            .scalars().all()
        )
        for rec in records:
            # Match by jenis_kemampuan to the fixed row, fallback to sequential
            row = _KEPUASAN_ROW.get(rec.jenis_kemampuan)
            if row is None:
                continue
            self.safe_write(ws, f"C{row}", rec.sangat_baik)
            self.safe_write(ws, f"D{row}", rec.baik)
            self.safe_write(ws, f"E{row}", rec.cukup)
            self.safe_write(ws, f"F{row}", rec.kurang)
            self.safe_write(ws, f"G{row}", rec.rencana_tindak_lanjut)

    def _fill_penelitian_mahasiswa(self) -> None:
        _sheet_map = {
            "penelitian":      ("6h1", 11),
            "tesis_disertasi": ("6h2", 6),
            "pkm":             ("6i",  6),
        }
        for jenis, (sheet_name, start_row) in _sheet_map.items():
            if not self.sheet_applies(sheet_name):
                continue
            ws = self.wb[sheet_name]
            records = (
                self.db.execute(
                    select(LkpsPenelitianMahasiswa)
                    .where(
                        LkpsPenelitianMahasiswa.submission_id == self.submission.id,
                        LkpsPenelitianMahasiswa.jenis == jenis,
                    )
                    .order_by(LkpsPenelitianMahasiswa.no)
                )
                .scalars().all()
            )
            for i, rec in enumerate(records):
                row = start_row + i
                self.safe_write(ws, f"B{row}", rec.nama_dosen)
                self.safe_write(ws, f"C{row}", rec.tema_penelitian)
                self.safe_write(ws, f"D{row}", rec.nama_mahasiswa)
                self.safe_write(ws, f"E{row}", rec.judul_kegiatan)
                self.safe_write(ws, f"F{row}", rec.tahun)
