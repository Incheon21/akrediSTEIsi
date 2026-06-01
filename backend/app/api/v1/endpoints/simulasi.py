from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.lkps import (
    LkpsKurikulum,
    LkpsMahasiswaAktif,
    LkpsMkBasicScience,
    LkpsPenelitianMahasiswa,
    LkpsPenelitianSummary,
    LkpsPenggunaanDana,
    LkpsPkmSummary,
    LkpsSubmission,
)
from app.models.program_studi import ProgramStudi
from app.models.simulasi import MatriksAkreditasi, SkorManualSimulasi
from app.models.target_akreditasi import TargetAkreditasi
from app.schemas.simulasi import SimulasiRequest, SimulasiResponse
from app.services.simulasi import SimulasiService
from app.utils.dependencies import get_db

router = APIRouter()

AUTOMATED_INDICATOR_CODES = {"9", "10", "11", "18", "19", "23", "25"}
SCORING_GROUPS = [
    {
        "id": "G1",
        "urutan": 1,
        "nama": "Diferensiasi Misi",
        "deskripsi": "Visi, Misi, Tujuan, dan Strategi",
        "kode_awal": 1,
        "kode_akhir": 3,
    },
    {
        "id": "G2",
        "urutan": 2,
        "nama": "Akuntabilitas",
        "deskripsi": "Tata pamong, tata kelola, kerja sama, dan keuangan.",
        "kode_awal": 4,
        "kode_akhir": 11,
    },
    {
        "id": "G3",
        "urutan": 3,
        "nama": "Relevansi Pendidikan, Penelitian, dan PkM",
        "deskripsi": "Profil lulusan, CPL, kurikulum, pembelajaran, penelitian, dan PkM.",
        "kode_awal": 12,
        "kode_akhir": 25,
    },
    {
        "id": "G4",
        "urutan": 4,
        "nama": "Sumber Daya Manusia",
        "deskripsi": "Profil dosen, tenaga kependidikan, beban kerja, dan kinerja DTPS.",
        "kode_awal": 26,
        "kode_akhir": 37,
    },
    {
        "id": "G5",
        "urutan": 5,
        "nama": "Sarana, Prasarana, dan K3L",
        "deskripsi": "Kecukupan sarana-prasarana dan keselamatan kesehatan kerja lingkungan.",
        "kode_awal": 38,
        "kode_akhir": 39,
    },
    {
        "id": "G6",
        "urutan": 6,
        "nama": "Mahasiswa dan Luaran Mahasiswa",
        "deskripsi": "Profil mahasiswa, prestasi, masa studi, kelulusan, dan luaran lulusan.",
        "kode_awal": 40,
        "kode_akhir": 52,
    },
    {
        "id": "G7",
        "urutan": 7,
        "nama": "Sistem Penjaminan Mutu dan Pengembangan Berkelanjutan",
        "deskripsi": "Siklus PPEPP, analisis lingkungan, dan strategi pengembangan berkelanjutan.",
        "kode_awal": 53,
        "kode_akhir": 60,
    },
]
SCORING_SUBSECTIONS = [
    {
        "id": "G1-1",
        "group_id": "G1",
        "urutan": 1,
        "kode": "1.1",
        "nama": "Visi, Misi, Tujuan, dan Strategi",
        "deskripsi": "Diferensiasi misi dan ketercapaian VMTS.",
        "kode_awal": 1,
        "kode_akhir": 3,
    },
    {
        "id": "G2-1",
        "group_id": "G2",
        "urutan": 1,
        "kode": "2.1",
        "nama": "Tata Pamong dan Tata Kelola",
        "deskripsi": "Struktur, kepemimpinan, dan kapabilitas tata kelola.",
        "kode_awal": 4,
        "kode_akhir": 5,
    },
    {
        "id": "G2-2",
        "group_id": "G2",
        "urutan": 2,
        "kode": "2.2",
        "nama": "Kerjasama",
        "deskripsi": "Relevansi dan pelaksanaan kerja sama tridarma.",
        "kode_awal": 6,
        "kode_akhir": 7,
    },
    {
        "id": "G2-3",
        "group_id": "G2",
        "urutan": 3,
        "kode": "2.3",
        "nama": "Keuangan",
        "deskripsi": "Pengelolaan dana pendidikan, penelitian, dan PkM.",
        "kode_awal": 8,
        "kode_akhir": 11,
    },
    {
        "id": "G3-1",
        "group_id": "G3",
        "urutan": 1,
        "kode": "3.1",
        "nama": "Pendidikan",
        "deskripsi": "Profil lulusan, CPL, kurikulum, dan proses pembelajaran.",
        "kode_awal": 12,
        "kode_akhir": 21,
    },
    {
        "id": "G3-2",
        "group_id": "G3",
        "urutan": 2,
        "kode": "3.2",
        "nama": "Penelitian",
        "deskripsi": "Relevansi penelitian dan pelibatan mahasiswa.",
        "kode_awal": 22,
        "kode_akhir": 23,
    },
    {
        "id": "G3-3",
        "group_id": "G3",
        "urutan": 3,
        "kode": "3.3",
        "nama": "Pengabdian kepada Masyarakat (PkM)",
        "deskripsi": "Relevansi PkM dan pelibatan mahasiswa.",
        "kode_awal": 24,
        "kode_akhir": 25,
    },
    {
        "id": "G4-1",
        "group_id": "G4",
        "urutan": 1,
        "kode": "4.1",
        "nama": "Profil Dosen dan Tenaga Kependidikan",
        "deskripsi": "Kecukupan, kualifikasi, jabatan akademik, dan tenaga kependidikan.",
        "kode_awal": 26,
        "kode_akhir": 29,
    },
    {
        "id": "G4-2",
        "group_id": "G4",
        "urutan": 2,
        "kode": "4.2",
        "nama": "Beban Kerja dan Kinerja DTPS",
        "deskripsi": "Beban kerja, penelitian, PkM, publikasi, luaran, dan rekognisi DTPS.",
        "kode_awal": 30,
        "kode_akhir": 37,
    },
    {
        "id": "G5-1",
        "group_id": "G5",
        "urutan": 1,
        "kode": "5.1",
        "nama": "Sarana, Prasarana, dan K3L",
        "deskripsi": "Kecukupan sarana-prasarana serta keselamatan kesehatan kerja lingkungan.",
        "kode_awal": 38,
        "kode_akhir": 39,
    },
    {
        "id": "G6-1",
        "group_id": "G6",
        "urutan": 1,
        "kode": "6.1",
        "nama": "Mahasiswa",
        "deskripsi": "Profil, rasio, dan kualitas mahasiswa.",
        "kode_awal": 40,
        "kode_akhir": 41,
    },
    {
        "id": "G6-2",
        "group_id": "G6",
        "urutan": 2,
        "kode": "6.2",
        "nama": "Capaian Pembelajaran dan Prestasi Mahasiswa",
        "deskripsi": "IPK, prestasi, masa studi, dan kelulusan.",
        "kode_awal": 42,
        "kode_akhir": 45,
    },
    {
        "id": "G6-3",
        "group_id": "G6",
        "urutan": 3,
        "kode": "6.3",
        "nama": "Luaran Mahasiswa",
        "deskripsi": "Publikasi ilmiah serta luaran penelitian dan PkM mahasiswa.",
        "kode_awal": 46,
        "kode_akhir": 47,
    },
    {
        "id": "G6-4",
        "group_id": "G6",
        "urutan": 4,
        "kode": "6.4",
        "nama": "Tracer Study dan Luaran Lulusan",
        "deskripsi": "Tracer study, waktu tunggu, kesesuaian bidang kerja, dan kepuasan pengguna.",
        "kode_awal": 48,
        "kode_akhir": 52,
    },
    {
        "id": "G7-1",
        "group_id": "G7",
        "urutan": 1,
        "kode": "7.1",
        "nama": "Sistem Penjaminan Mutu",
        "deskripsi": "Unit SPM, indikator mutu, keterlaksanaan, evaluasi, dan kepuasan.",
        "kode_awal": 53,
        "kode_akhir": 57,
    },
    {
        "id": "G7-2",
        "group_id": "G7",
        "urutan": 2,
        "kode": "B",
        "nama": "Program Pengembangan Berkelanjutan",
        "deskripsi": "Analisis lingkungan, tujuan strategis, dan program pengembangan.",
        "kode_awal": 58,
        "kode_akhir": 60,
    },
]


class ManualScorePayload(BaseModel):
    scores: dict[str, float] = Field(default_factory=dict)


@router.post("/hitung", response_model=SimulasiResponse)
def hitung_simulasi(request: SimulasiRequest, db: Session = Depends(get_db)):
    try:
        service = SimulasiService(db)
        return service.process_simulasi(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan server")


def _avg(values) -> float:
    nums = [float(v or 0) for v in values]
    return sum(nums) / len(nums) if nums else 0.0


def _sum_years(rows) -> int:
    return sum(int((r.ts2 or 0) + (r.ts1 or 0) + (r.ts or 0)) for r in rows)


def _get_teknik_sarjana_matrix(db: Session) -> MatriksAkreditasi | None:
    return (
        db.query(MatriksAkreditasi)
        .filter(
            MatriksAkreditasi.lembaga == "TEKNIK",
            MatriksAkreditasi.jenjang == "SARJANA",
        )
        .first()
    )


def _scoring_group_for_code(kode_indikator: str) -> dict:
    try:
        kode = int(kode_indikator)
    except (TypeError, ValueError):
        kode = 0

    for group in SCORING_GROUPS:
        if group["kode_awal"] <= kode <= group["kode_akhir"]:
            return group

    return {
        "id": "G0",
        "urutan": 0,
        "nama": "Belum Terpetakan",
        "deskripsi": "Indikator belum masuk rentang kelompok pada matriks penilaian.",
        "kode_awal": kode,
        "kode_akhir": kode,
    }


def _scoring_subsection_for_code(kode_indikator: str) -> dict:
    try:
        kode = int(kode_indikator)
    except (TypeError, ValueError):
        kode = 0

    for subsection in SCORING_SUBSECTIONS:
        if subsection["kode_awal"] <= kode <= subsection["kode_akhir"]:
            return subsection

    return {
        "id": "G0-0",
        "group_id": "G0",
        "urutan": 0,
        "kode": "-",
        "nama": "Belum Terpetakan",
        "deskripsi": "Indikator belum masuk rentang sub bab pada matriks penilaian.",
        "kode_awal": kode,
        "kode_akhir": kode,
    }


def _subsection_payload(subsection: dict) -> dict:
    return {
        "id": subsection["id"],
        "group_id": subsection["group_id"],
        "urutan": subsection["urutan"],
        "kode": subsection["kode"],
        "nama": subsection["nama"],
        "deskripsi": subsection["deskripsi"],
        "kode_awal": subsection["kode_awal"],
        "kode_akhir": subsection["kode_akhir"],
        "jumlah_indikator": 0,
        "jumlah_manual": 0,
        "jumlah_manual_terisi": 0,
        "jumlah_otomatis": 0,
    }


def _group_payload(group: dict) -> dict:
    return {
        "id": group["id"],
        "urutan": group["urutan"],
        "nama": group["nama"],
        "deskripsi": group["deskripsi"],
        "kode_awal": group["kode_awal"],
        "kode_akhir": group["kode_akhir"],
        "sub_bab": [
            _subsection_payload(subsection)
            for subsection in SCORING_SUBSECTIONS
            if subsection["group_id"] == group["id"]
        ],
    }


@router.put("/manual/{submission_id}")
def simpan_skor_manual(
    submission_id: UUID,
    payload: ManualScorePayload,
    db: Session = Depends(get_db),
):
    submission = (
        db.query(LkpsSubmission)
        .filter(LkpsSubmission.id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission LKPS tidak ditemukan")

    matriks = _get_teknik_sarjana_matrix(db)
    if not matriks:
        raise HTTPException(status_code=404, detail="Matriks simulasi tidak ditemukan")

    valid_manual_codes = {
        indikator.kode_indikator
        for komponen in matriks.komponen
        for indikator in komponen.indikator
        if indikator.kode_indikator not in AUTOMATED_INDICATOR_CODES
    }

    normalized_scores: dict[str, float] = {}
    for kode, skor in payload.scores.items():
        kode_indikator = str(kode)
        if kode_indikator not in valid_manual_codes:
            raise HTTPException(
                status_code=400,
                detail=f"Indikator {kode_indikator} tidak bisa diisi manual",
            )
        if skor < 0 or skor > 4:
            raise HTTPException(
                status_code=400,
                detail=f"Skor indikator {kode_indikator} harus berada pada rentang 0-4",
            )
        normalized_scores[kode_indikator] = float(skor)

    existing_rows = {
        row.kode_indikator: row
        for row in db.query(SkorManualSimulasi)
        .filter(SkorManualSimulasi.submission_id == submission_id)
        .all()
    }

    for kode_indikator, row in existing_rows.items():
        if kode_indikator not in normalized_scores:
            db.delete(row)

    for kode_indikator, skor in normalized_scores.items():
        row = existing_rows.get(kode_indikator)
        if row:
            row.skor = skor
        else:
            db.add(
                SkorManualSimulasi(
                    submission_id=submission_id,
                    kode_indikator=kode_indikator,
                    skor=skor,
                )
            )

    db.commit()

    return {
        "submission_id": str(submission_id),
        "jumlah_tersimpan": len(normalized_scores),
        "scores": normalized_scores,
    }


@router.get("/otomatis/{prodi_id}")
def hitung_simulasi_otomatis(
    prodi_id: UUID,
    tahun: int | None = None,
    db: Session = Depends(get_db),
):
    prodi = db.query(ProgramStudi).filter(ProgramStudi.id == prodi_id).first()
    if not prodi:
        raise HTTPException(status_code=404, detail="Program studi tidak ditemukan")

    target = None
    if tahun:
        target = (
            db.query(TargetAkreditasi)
            .filter(
                TargetAkreditasi.program_studi_id == prodi_id,
                TargetAkreditasi.tahun_akreditasi == tahun,
            )
            .first()
        )
    else:
        target = (
            db.query(TargetAkreditasi)
            .filter(
                TargetAkreditasi.program_studi_id == prodi_id,
                TargetAkreditasi.is_aktif == True,
            )
            .first()
        )

    tahun_ts = target.tahun_akreditasi if target else tahun
    if not tahun_ts:
        raise HTTPException(status_code=400, detail="Tahun akreditasi tidak ditemukan")

    submission = (
        db.query(LkpsSubmission)
        .filter(
            LkpsSubmission.program_studi_id == prodi_id,
            LkpsSubmission.tahun_ts == tahun_ts,
        )
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission LKPS tidak ditemukan")

    matriks = _get_teknik_sarjana_matrix(db)
    if not matriks:
        raise HTTPException(status_code=404, detail="Matriks simulasi tidak ditemukan")

    service = SimulasiService(db)
    indikator_by_code = {
        indikator.kode_indikator: indikator
        for komponen in matriks.komponen
        for indikator in komponen.indikator
    }
    component_counts = {
        komponen.id: len(komponen.indikator) or 1 for komponen in matriks.komponen
    }

    dana_rows = {
        row.kode: row
        for row in db.query(LkpsPenggunaanDana)
        .filter(LkpsPenggunaanDana.submission_id == submission.id)
        .all()
    }

    def avg_ps_dana(*kodes: str) -> float:
        rows = [dana_rows[kode] for kode in kodes if kode in dana_rows]
        if not rows:
            return 0.0
        yearly_totals = [
            sum(float(row.ps_ts2 or 0) for row in rows),
            sum(float(row.ps_ts1 or 0) for row in rows),
            sum(float(row.ps_ts or 0) for row in rows),
        ]
        return _avg(yearly_totals)

    mahasiswa = (
        db.query(LkpsMahasiswaAktif)
        .filter(
            LkpsMahasiswaAktif.submission_id == submission.id,
            LkpsMahasiswaAktif.prodi_diakreditasi == True,
        )
        .first()
    )
    avg_mahasiswa = (
        _avg([mahasiswa.aktif_ts2, mahasiswa.aktif_ts1, mahasiswa.aktif_ts])
        if mahasiswa
        else 0.0
    )

    kurikulum_rows = (
        db.query(LkpsKurikulum)
        .filter(LkpsKurikulum.submission_id == submission.id)
        .all()
    )
    total_sks = sum(
        float((row.sks_kuliah or 0) + (row.sks_seminar or 0) + (row.sks_praktikum or 0))
        for row in kurikulum_rows
    )
    sks_praktikum = sum(float(row.sks_praktikum or 0) for row in kurikulum_rows)

    basic_science_sks = sum(
        float(row.jumlah_sks or 0)
        for row in db.query(LkpsMkBasicScience)
        .filter(LkpsMkBasicScience.submission_id == submission.id)
        .all()
    )

    penelitian_total = _sum_years(
        db.query(LkpsPenelitianSummary)
        .filter(LkpsPenelitianSummary.submission_id == submission.id)
        .all()
    )
    penelitian_mhs = (
        db.query(LkpsPenelitianMahasiswa)
        .filter(
            LkpsPenelitianMahasiswa.submission_id == submission.id,
            LkpsPenelitianMahasiswa.jenis == "penelitian",
        )
        .count()
    )

    pkm_total = _sum_years(
        db.query(LkpsPkmSummary)
        .filter(LkpsPkmSummary.submission_id == submission.id)
        .all()
    )
    pkm_mhs = (
        db.query(LkpsPenelitianMahasiswa)
        .filter(
            LkpsPenelitianMahasiswa.submission_id == submission.id,
            LkpsPenelitianMahasiswa.jenis == "pkm",
        )
        .count()
    )

    auto_values = {
        "9": avg_ps_dana(
            "biaya_dosen",
            "biaya_tendik",
            "biaya_op_pembelajaran",
            "biaya_op_tidak_langsung",
            "biaya_praktik_ppi",
            "biaya_investasi",
            "biaya_kemahasiswaan",
        )
        / avg_mahasiswa
        if avg_mahasiswa
        else 0.0,
        "10": avg_ps_dana("biaya_penelitian"),
        "11": avg_ps_dana("biaya_pkm"),
        "18": (sks_praktikum / total_sks) if total_sks else 0.0,
        "19": basic_science_sks,
        "23": (penelitian_mhs / penelitian_total) if penelitian_total else 0.0,
        "25": (pkm_mhs / pkm_total) if pkm_total else 0.0,
    }
    auto_sources = {
        "9": "Turunan LKPS 2b: rata-rata total biaya pendidikan PS baris 7-13 dibagi rata-rata mahasiswa aktif.",
        "10": "LKPS 2b: rata-rata biaya penelitian PS.",
        "11": "LKPS 2b: rata-rata biaya PkM PS.",
        "18": "LKPS 3a1: SKS praktikum dibagi total SKS kurikulum.",
        "19": "LKPS 3a4: total SKS basic science dan matematika.",
        "23": "LKPS 6h1 dan 3b: penelitian melibatkan mahasiswa dibagi total penelitian DTPS.",
        "25": "LKPS 6i dan 3c: PkM melibatkan mahasiswa dibagi total PkM DTPS.",
    }
    manual_scores = {
        row.kode_indikator: row.skor
        for row in db.query(SkorManualSimulasi)
        .filter(SkorManualSimulasi.submission_id == submission.id)
        .all()
    }

    indikator_results = []
    all_indicator_results = []
    automated_codes = set(auto_values)
    total_score = 0.0
    manual_score = 0.0
    max_automated_score = 0.0
    breakdown = {}

    for komponen in matriks.komponen:
        for indikator in sorted(
            komponen.indikator,
            key=lambda item: int(item.kode_indikator)
            if item.kode_indikator.isdigit()
            else item.kode_indikator,
        ):
            max_contribution = 4.0 * komponen.bobot / component_counts[komponen.id]
            saved_manual_score = manual_scores.get(indikator.kode_indikator)
            scoring_group = _scoring_group_for_code(indikator.kode_indikator)
            scoring_subsection = _scoring_subsection_for_code(indikator.kode_indikator)
            manual_contribution = 0.0
            if indikator.kode_indikator not in automated_codes and saved_manual_score is not None:
                manual_contribution = (
                    min(4.0, max(0.0, saved_manual_score)) / 4.0
                ) * max_contribution
                manual_score += manual_contribution
                breakdown[komponen.nama] = (
                    breakdown.get(komponen.nama, 0.0) + manual_contribution
                )

            all_indicator_results.append(
                {
                    "kode_indikator": indikator.kode_indikator,
                    "nama_indikator": indikator.nama_indikator,
                    "komponen": komponen.nama,
                    "mode": "AUTO_LKPS"
                    if indikator.kode_indikator in automated_codes
                    else "MANUAL",
                    "kontribusi_maks": round(max_contribution, 2),
                    "skor_manual": round(saved_manual_score, 2)
                    if saved_manual_score is not None
                    else None,
                    "kontribusi_manual": round(manual_contribution, 2),
                    "kelompok_penilaian": scoring_group["id"],
                    "kelompok_urutan": scoring_group["urutan"],
                    "kelompok_nama": scoring_group["nama"],
                    "kelompok_deskripsi": scoring_group["deskripsi"],
                    "subbab_penilaian": scoring_subsection["id"],
                    "subbab_urutan": scoring_subsection["urutan"],
                    "subbab_kode": scoring_subsection["kode"],
                    "subbab_nama": scoring_subsection["nama"],
                    "subbab_deskripsi": scoring_subsection["deskripsi"],
                }
            )

    for kode, nilai_input in auto_values.items():
        indikator = indikator_by_code.get(kode)
        if not indikator or not indikator.komponen:
            continue

        raw_score = service._hitung_skor_mentah(indikator, nilai_input)
        contribution = (
            raw_score * indikator.komponen.bobot / component_counts[indikator.komponen_id]
        )
        max_contribution = (
            4.0 * indikator.komponen.bobot / component_counts[indikator.komponen_id]
        )
        scoring_group = _scoring_group_for_code(kode)
        scoring_subsection = _scoring_subsection_for_code(kode)
        total_score += contribution
        max_automated_score += max_contribution
        breakdown[indikator.komponen.nama] = (
            breakdown.get(indikator.komponen.nama, 0.0) + contribution
        )

        indikator_results.append(
            {
                "kode_indikator": kode,
                "nama_indikator": indikator.nama_indikator,
                "komponen": indikator.komponen.nama,
                "nilai_input": round(nilai_input, 4),
                "skor_mentah": round(raw_score, 2),
                "kontribusi": round(contribution, 2),
                "kontribusi_maks": round(max_contribution, 2),
                "sumber_data": auto_sources.get(kode, "LKPS"),
                "kelompok_penilaian": scoring_group["id"],
                "kelompok_urutan": scoring_group["urutan"],
                "kelompok_nama": scoring_group["nama"],
                "kelompok_deskripsi": scoring_group["deskripsi"],
                "subbab_penilaian": scoring_subsection["id"],
                "subbab_urutan": scoring_subsection["urutan"],
                "subbab_kode": scoring_subsection["kode"],
                "subbab_nama": scoring_subsection["nama"],
                "subbab_deskripsi": scoring_subsection["deskripsi"],
            }
        )

    group_summaries = [_group_payload(group) for group in SCORING_GROUPS]
    summary_by_id = {group["id"]: group for group in group_summaries}
    subsection_summary_by_id = {
        subsection["id"]: subsection
        for group in group_summaries
        for subsection in group["sub_bab"]
    }
    for group in group_summaries:
        group.update(
            {
                "jumlah_indikator": 0,
                "jumlah_manual": 0,
                "jumlah_manual_terisi": 0,
                "jumlah_otomatis": 0,
            }
        )

    for item in all_indicator_results:
        group = summary_by_id.get(item["kelompok_penilaian"])
        if not group:
            continue
        subsection = subsection_summary_by_id.get(item["subbab_penilaian"])
        group["jumlah_indikator"] += 1
        if subsection:
            subsection["jumlah_indikator"] += 1
        if item["mode"] == "AUTO_LKPS":
            group["jumlah_otomatis"] += 1
            if subsection:
                subsection["jumlah_otomatis"] += 1
        else:
            group["jumlah_manual"] += 1
            if subsection:
                subsection["jumlah_manual"] += 1
            if item["skor_manual"] is not None:
                group["jumlah_manual_terisi"] += 1
                if subsection:
                    subsection["jumlah_manual_terisi"] += 1

    return {
        "program_studi": prodi.nama,
        "tahun_ts": tahun_ts,
        "submission_id": str(submission.id),
        "nilai_otomatis": round(total_score, 2),
        "nilai_manual": round(manual_score, 2),
        "nilai_total": round(total_score + manual_score, 2),
        "nilai_maksimum_total": 400.0,
        "nilai_maksimum_otomatis": round(max_automated_score, 2),
        "jumlah_indikator_otomatis": len(indikator_results),
        "jumlah_indikator_manual_terisi": len(manual_scores),
        "breakdown_skor": {key: round(value, 2) for key, value in breakdown.items()},
        "indikator": indikator_results,
        "semua_indikator": all_indicator_results,
        "kelompok_penilaian": group_summaries,
        "catatan": "Skor ini hanya menghitung indikator matriks yang datanya sudah bisa diturunkan otomatis dari LKPS.",
    }
