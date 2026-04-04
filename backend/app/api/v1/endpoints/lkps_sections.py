from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Type

from app.db import Base
from app.models.lkps import (
    LkpsBebanKerjaDosen,
    LkpsCapstoneDesign,
    LkpsDosenProfil,
    LkpsIpkLulusan,
    LkpsIntegrasiPenelitian,
    LkpsK3lDokumen,
    LkpsK3lFasilitas,
    LkpsKepuasanPengguna,
    LkpsKerjasama,
    LkpsKesesuaianKerja,
    LkpsKinerjaDtps,
    LkpsKurikulum,
    LkpsLuaranPenelitian,
    LkpsMahasiswaAktif,
    LkpsMasaStudi,
    LkpsMkBasicScience,
    LkpsPembimbingLapangan,
    LkpsPenelitianMahasiswa,
    LkpsPenelitianSummary,
    LkpsPenggunaanDana,
    LkpsPkmSummary,
    LkpsPrasarana,
    LkpsPrestasiMahasiswa,
    LkpsProdukJasa,
    LkpsPublikasiIlmiah,
    LkpsRekognisiDtps,
    LkpsSitasiDtps,
    LkpsSpmiDokumen,
    LkpsSpmiPelaksanaan,
    LkpsTempatKerja,
    LkpsTenagaKependidikan,
    LkpsVmts,
    LkpsWaktuTunggu,
)


@dataclass(frozen=True)
class SectionBinding:
    code: str
    model: Type[Base]
    enforced_values: Dict[str, Any] = field(default_factory=dict)
    order_by: Tuple[str, ...] = field(default_factory=tuple)
    label: str = ""


def _binding(
    code: str,
    model: Type[Base],
    *,
    enforced: Dict[str, Any] | None = None,
    order: Tuple[str, ...] | None = None,
    label: str = "",
) -> SectionBinding:
    return SectionBinding(
        code=code,
        model=model,
        enforced_values=enforced or {},
        order_by=order or tuple(),
        label=label,
    )


LKPS_SECTION_BINDINGS: Dict[str, SectionBinding] = {
    "1": _binding("1", LkpsVmts, order=("no",), label="VMTS"),
    "2a1": _binding(
        "2a1",
        LkpsKerjasama,
        enforced={"jenis": "pendidikan"},
        order=("lembaga_mitra",),
        label="Kerjasama Pendidikan",
    ),
    "2a2": _binding(
        "2a2",
        LkpsKerjasama,
        enforced={"jenis": "penelitian"},
        order=("lembaga_mitra",),
        label="Kerjasama Penelitian",
    ),
    "2a3": _binding(
        "2a3",
        LkpsKerjasama,
        enforced={"jenis": "pkm"},
        order=("lembaga_mitra",),
        label="Kerjasama PKM",
    ),
    "2b": _binding("2b", LkpsPenggunaanDana, order=("kode",), label="Penggunaan Dana"),
    "3a1": _binding(
        "3a1",
        LkpsKurikulum,
        order=("semester", "kode_mk"),
        label="Daftar Mata Kuliah",
    ),
    "3a3": _binding(
        "3a3",
        LkpsIntegrasiPenelitian,
        order=("nama_dosen",),
        label="Integrasi Penelitian",
    ),
    "3a4": _binding(
        "3a4",
        LkpsMkBasicScience,
        order=("semester", "nama_mk"),
        label="Basic Science",
    ),
    "3a5": _binding(
        "3a5",
        LkpsCapstoneDesign,
        order=("semester", "nama_mk_capstone"),
        label="Capstone Design",
    ),
    "3b": _binding("3b", LkpsPenelitianSummary, order=("kode_sumber",), label="Penelitian DTPS"),
    "3c": _binding("3c", LkpsPkmSummary, order=("kode_sumber",), label="PkM DTPS"),
    "4a": _binding("4a", LkpsDosenProfil, order=("nama_dosen",), label="Profil DTPS"),
    "4b": _binding("4b", LkpsTenagaKependidikan, order=("nama",), label="Tendik"),
    "4c": _binding("4c", LkpsBebanKerjaDosen, order=("nama_dosen",), label="Beban Kerja"),
    "4d": _binding(
        "4d",
        LkpsPublikasiIlmiah,
        enforced={"sumber": "dtps", "jenis_program": "akademik"},
        order=("kode_publikasi",),
        label="Publikasi DTPS Akademik",
    ),
    "4e": _binding(
        "4e",
        LkpsPublikasiIlmiah,
        enforced={"sumber": "dtps", "jenis_program": "vokasi"},
        order=("kode_publikasi",),
        label="Publikasi DTPS Vokasi",
    ),
    "4f-1": _binding(
        "4f-1",
        LkpsLuaranPenelitian,
        enforced={"sumber": "dtps", "jenis_luaran": "paten"},
        order=("tanggal", "judul"),
        label="Luaran DTPS - Paten",
    ),
    "4f-2": _binding(
        "4f-2",
        LkpsLuaranPenelitian,
        enforced={"sumber": "dtps", "jenis_luaran": "hak_cipta"},
        order=("tanggal", "judul"),
        label="Luaran DTPS - Hak Cipta",
    ),
    "4f-3": _binding(
        "4f-3",
        LkpsLuaranPenelitian,
        enforced={"sumber": "dtps", "jenis_luaran": "teknologi"},
        order=("tanggal", "judul"),
        label="Luaran DTPS - Teknologi",
    ),
    "4f-4": _binding(
        "4f-4",
        LkpsLuaranPenelitian,
        enforced={"sumber": "dtps", "jenis_luaran": "buku"},
        order=("tanggal", "judul"),
        label="Luaran DTPS - Buku",
    ),
    "4g": _binding(
        "4g",
        LkpsProdukJasa,
        enforced={"sumber": "dtps"},
        order=("nama_produk_jasa",),
        label="Produk/Jasa DTPS",
    ),
    "4h": _binding("4h", LkpsKinerjaDtps, order=("nama_dosen",), label="Kinerja DTPS"),
    "4i": _binding("4i", LkpsSitasiDtps, order=("nama_dosen",), label="Sitasi DTPS"),
    "4j": _binding("4j", LkpsRekognisiDtps, order=("nama_dosen",), label="Rekognisi DTPS"),
    "4k": _binding(
        "4k",
        LkpsPembimbingLapangan,
        order=("nama",),
        label="Pembimbing Lapangan",
    ),
    "5a": _binding("5a", LkpsPrasarana, order=("nama_prasarana",), label="Prasarana"),
    "5b": _binding("5b", LkpsK3lDokumen, order=("no",), label="Dokumen K3L"),
    "5c": _binding("5c", LkpsK3lFasilitas, order=("nama_sarana",), label="Fasilitas K3L"),
    "6a": _binding(
        "6a",
        LkpsMahasiswaAktif,
        order=("no",),
        label="Mahasiswa Aktif",
    ),
    "6b": _binding("6b", LkpsIpkLulusan, order=("periode",), label="IPK Lulusan"),
    "6c1": _binding(
        "6c1",
        LkpsPrestasiMahasiswa,
        enforced={"jenis": "akademik"},
        order=("no",),
        label="Prestasi Akademik",
    ),
    "6c2": _binding(
        "6c2",
        LkpsPrestasiMahasiswa,
        enforced={"jenis": "non_akademik"},
        order=("no",),
        label="Prestasi Non-Akademik",
    ),
    "6d": _binding("6d", LkpsMasaStudi, order=("jenis_program", "tahun_masuk"), label="Masa Studi"),
    "6e1": _binding(
        "6e1",
        LkpsPublikasiIlmiah,
        enforced={"sumber": "mahasiswa", "jenis_program": "akademik"},
        order=("kode_publikasi",),
        label="Publikasi Mahasiswa Akademik",
    ),
    "6e2": _binding(
        "6e2",
        LkpsPublikasiIlmiah,
        enforced={"sumber": "mahasiswa", "jenis_program": "vokasi"},
        order=("kode_publikasi",),
        label="Publikasi Mahasiswa Vokasi",
    ),
    "6e3-1": _binding(
        "6e3-1",
        LkpsLuaranPenelitian,
        enforced={"sumber": "mahasiswa", "jenis_luaran": "paten"},
        order=("tanggal", "judul"),
        label="Luaran Mahasiswa - Paten",
    ),
    "6e3-2": _binding(
        "6e3-2",
        LkpsLuaranPenelitian,
        enforced={"sumber": "mahasiswa", "jenis_luaran": "hak_cipta"},
        order=("tanggal", "judul"),
        label="Luaran Mahasiswa - Hak Cipta",
    ),
    "6e3-3": _binding(
        "6e3-3",
        LkpsLuaranPenelitian,
        enforced={"sumber": "mahasiswa", "jenis_luaran": "teknologi"},
        order=("tanggal", "judul"),
        label="Luaran Mahasiswa - Teknologi",
    ),
    "6e3-4": _binding(
        "6e3-4",
        LkpsLuaranPenelitian,
        enforced={"sumber": "mahasiswa", "jenis_luaran": "buku"},
        order=("tanggal", "judul"),
        label="Luaran Mahasiswa - Buku",
    ),
    "6e4": _binding(
        "6e4",
        LkpsProdukJasa,
        enforced={"sumber": "mahasiswa"},
        order=("nama_produk_jasa",),
        label="Produk/Jasa Mahasiswa",
    ),
    "6f1": _binding("6f1", LkpsWaktuTunggu, order=("jenis_program", "tahun_lulus"), label="Waktu Tunggu"),
    "6f2": _binding("6f2", LkpsKesesuaianKerja, order=("tahun_lulus",), label="Kesesuaian Kerja"),
    "6g1": _binding("6g1", LkpsTempatKerja, order=("tahun_lulus",), label="Tempat Kerja"),
    "6g2": _binding("6g2", LkpsKepuasanPengguna, order=("no",), label="Kepuasan Pengguna"),
    "6h1": _binding(
        "6h1",
        LkpsPenelitianMahasiswa,
        enforced={"jenis": "penelitian"},
        order=("no",),
        label="Penelitian dengan Mahasiswa",
    ),
    "6h2": _binding(
        "6h2",
        LkpsPenelitianMahasiswa,
        enforced={"jenis": "tesis_disertasi"},
        order=("no",),
        label="Tesis/Disertasi",
    ),
    "6i": _binding(
        "6i",
        LkpsPenelitianMahasiswa,
        enforced={"jenis": "pkm"},
        order=("no",),
        label="PkM dengan Mahasiswa",
    ),
    "7a": _binding("7a", LkpsSpmiDokumen, order=("no",), label="SPMI Dokumen"),
    "7b": _binding("7b", LkpsSpmiPelaksanaan, order=("no",), label="SPMI Pelaksanaan"),
}


def get_section_binding(code: str) -> SectionBinding | None:
    return LKPS_SECTION_BINDINGS.get(code)
