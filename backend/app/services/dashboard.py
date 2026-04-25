from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.evidence import Evidence, EvidenceIndikator
from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.lkps import (
    LkpsBebanKerjaDosen,
    LkpsCapstoneDesign,
    LkpsDosenProfil,
    LkpsIntegrasiPenelitian,
    LkpsIpkLulusan,
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
    LkpsSubmission,
    LkpsTempatKerja,
    LkpsTenagaKependidikan,
    LkpsVmts,
    LkpsWaktuTunggu,
)
from app.models.narasi_led import NarasiLED
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi

KRITERIA_LKPS_MODELS = {
    "C1": [LkpsVmts],
    "C2": [LkpsKerjasama, LkpsPenggunaanDana],
    "C3": [
        LkpsKurikulum,
        LkpsIntegrasiPenelitian,
        LkpsMkBasicScience,
        LkpsCapstoneDesign,
        LkpsPenelitianSummary,
        LkpsPkmSummary,
    ],
    "C4": [
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
    ],
    "C5": [LkpsPrasarana, LkpsK3lDokumen, LkpsK3lFasilitas],
    "C6": [
        LkpsMahasiswaAktif,
        LkpsIpkLulusan,
        LkpsPrestasiMahasiswa,
        LkpsMasaStudi,
        LkpsWaktuTunggu,
        LkpsKesesuaianKerja,
        LkpsTempatKerja,
        LkpsKepuasanPengguna,
        LkpsPenelitianMahasiswa,
    ],
    "C7": [LkpsSpmiDokumen, LkpsSpmiPelaksanaan],
}


def get_dashboard_prodi_data(
    db: Session, prodi_id: UUID, tahun: int | None = None
) -> dict:
    prodi = db.query(ProgramStudi).filter(ProgramStudi.id == prodi_id).first()
    if not prodi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program Studi tidak ditemukan.",
        )

    # Get all target akreditasi years for this prodi
    all_targets = (
        db.query(TargetAkreditasi)
        .filter(TargetAkreditasi.program_studi_id == prodi_id)
        .all()
    )
    available_years = sorted(
        list(set([t.tahun_akreditasi for t in all_targets if t.tahun_akreditasi and t.is_aktif]))
    )

    if tahun:
        active_target = next(
            (t for t in all_targets if t.tahun_akreditasi == tahun and t.is_aktif), None
        )
    else:
        active_target = next((t for t in all_targets if t.is_aktif), None)

    aktif_akreditasi = active_target is not None
    current_year = active_target.tahun_akreditasi if active_target else (tahun or 0)

    lkps_submission = None
    if current_year:
        lkps_submission = (
            db.query(LkpsSubmission)
            .filter(
                LkpsSubmission.program_studi_id == prodi_id,
                LkpsSubmission.tahun_ts == current_year,
            )
            .first()
        )
        if not lkps_submission:
            try:
                lkps_submission = LkpsSubmission(
                    program_studi_id=prodi_id, tahun_ts=current_year, status="draft"
                )
                db.add(lkps_submission)
                db.commit()
                db.refresh(lkps_submission)
            except IntegrityError:
                db.rollback()
                lkps_submission = (
                    db.query(LkpsSubmission)
                    .filter(
                        LkpsSubmission.program_studi_id == prodi_id,
                        LkpsSubmission.tahun_ts == current_year,
                    )
                    .first()
                )

    target_score = (
        active_target.target_skor
        if active_target and active_target.target_skor
        else 3.5
    )
    deadline_str = (
        active_target.deadline.strftime("%d %B %Y")
        if active_target and active_target.deadline
        else "Belum Diatur"
    )

    kriteria_list_response = []
    all_kriteria = db.query(Kriteria).order_by(Kriteria.kode).all()

    for k in all_kriteria:
        indikators = db.query(Indikator).filter(Indikator.kriteria_id == k.id).all()

        lkps_ada = False
        led_ada = False
        has_evidence = False

        if active_target:
            ind_ids = [ind.id for ind in indikators]
            if ind_ids:
                # Check LKPS by querying actual tables
                lkps_ada = False
                if lkps_submission:
                    models = KRITERIA_LKPS_MODELS.get(k.kode, [])
                    for model in models:
                        if (
                            db.query(model)
                            .filter(model.submission_id == lkps_submission.id)
                            .first()
                        ):
                            lkps_ada = True
                            break

                # Check Evidence via junction table
                evid_count = (
                    db.query(EvidenceIndikator)
                    .filter(
                        EvidenceIndikator.indikator_id.in_(ind_ids),
                        EvidenceIndikator.target_akreditasi_id == active_target.id,
                    )
                    .count()
                )
                has_evidence = evid_count > 0

                # Check LED
                led_count = (
                    db.query(NarasiLED)
                    .filter(
                        NarasiLED.target_akreditasi_id == active_target.id,
                        NarasiLED.indikator_id.in_(ind_ids),
                    )
                    .count()
                )
                led_ada = led_count > 0

        # Status & Progress score per kriteria
        total_indicators = len(indikators)
        progress_score = 0

        if total_indicators > 0 and active_target:
            fulfilled_count = 0
            for ind in indikators:
                # indikator "selesai dikerjakan" jika sudah diberi Evidence, atau ada isian LKPS / LED
                has_lkps = lkps_ada

                has_led = (
                    db.query(NarasiLED)
                    .filter(
                        NarasiLED.target_akreditasi_id == active_target.id,
                        NarasiLED.indikator_id == ind.id,
                    )
                    .first()
                    is not None
                )

                # minimal led dan lkps ada
                if has_lkps and has_led:
                    fulfilled_count += 1

            progress_score = int((fulfilled_count / total_indicators) * 100)

        k_status = (
            "green"
            if progress_score >= 80
            else ("yellow" if progress_score >= 50 else "red")
        )
        k_status_label = (
            "Baik"
            if progress_score >= 80
            else ("Cukup" if progress_score >= 50 else "Buruk")
        )

        has_formula = any(ind.tipe_input == "formula" for ind in indikators)
        has_manual = any(ind.tipe_input == "manual" for ind in indikators)

        kriteria_list_response.append(
            {
                "id": k.kode.lower(),
                "name": f"{k.nama} ({k.kode})",
                "status": k_status,
                "status_label": k_status_label,
                "progress": progress_score,
                "has_lkps": True,
                "lkps_available": lkps_ada,
                "has_led": True,
                "led_available": led_ada,
                "has_evidence": has_evidence,
            }
        )

    # 4. dynamic recommendations and warnings
    pesan_rekomendasi = []
    early_warnings = []
    sisa_hari = 0

    if aktif_akreditasi and active_target.deadline:
        delta = active_target.deadline - date.today()
        sisa_hari = max(0, delta.days)

        if sisa_hari < 30 and sisa_hari > 0:
            early_warnings.append(f"Deadline akreditasi tersisa {sisa_hari} hari lagi!")
        elif sisa_hari == 0:
            early_warnings.append(
                "Deadline akreditasi telah lewat atau berakhir hari ini!"
            )

    if not aktif_akreditasi:
        pesan_rekomendasi.append(
            "Siklus akreditasi belum aktif. Hubungi Koordinator untuk mengaktifkan siklus baru."
        )
    else:
        # Check criteria completeness
        for k_resp in kriteria_list_response:
            if k_resp["progress"] < 100:
                kr_name = k_resp["name"].split(" ")[-1].strip("()")
                # Give specific recommendation based on which doc is missing
                if not k_resp["lkps_available"] and not k_resp["led_available"]:
                    pesan_rekomendasi.append(
                        f"Segera unggah data LKPS dan rumuskan Narasi LED pada kriteria {kr_name}."
                    )
                elif not k_resp["lkps_available"]:
                    pesan_rekomendasi.append(
                        f"Data LKPS belum lengkap untuk kriteria {kr_name}."
                    )
                elif not k_resp["led_available"]:
                    pesan_rekomendasi.append(
                        f"Narasi kualitatif LED belum selesai pada kriteria {kr_name}."
                    )

    # 5. Calculate overall progress percentages
    total_criteria = len(kriteria_list_response) if kriteria_list_response else 1
    lkps_completed_count = sum(1 for k in kriteria_list_response if k["lkps_available"])
    led_completed_count = sum(1 for k in kriteria_list_response if k["led_available"])
    evidence_completed_count = sum(
        1 for k in kriteria_list_response if k["has_evidence"]
    )

    lkpsPercent = int((lkps_completed_count / total_criteria) * 100)
    ledPercent = int((led_completed_count / total_criteria) * 100)
    dok_Percent = int((evidence_completed_count / total_criteria) * 100)

    if not aktif_akreditasi:
        lkpsPercent = ledPercent = dok_Percent = 0

    return {
        "program_studi_profile": {
            "name": prodi.nama,
            "degree": prodi.jenjang,
            "last_accreditation_status": prodi.akreditasi or "Belum Ada",
            "last_accreditation_year": prodi.tanggal_akreditasi.year
            if prodi.tanggal_akreditasi
            else 0,
            "is_active_accreditation": aktif_akreditasi,
            "prodi_status": prodi.status or "aktif",
        },
        "target_akreditasi_id": str(active_target.id) if active_target else "",
        "lkps_submission_id": str(lkps_submission.id) if lkps_submission else "",
        "current_year": current_year,
        "available_years": available_years,
        "criteria_list": kriteria_list_response,
        "recommendation_messages": pesan_rekomendasi,
        "early_warnings": early_warnings,
        # TODO Replace statis 0.0 dengan nilai kalkulasi asli LKPS
        "score_value": 0.0,
        "target_score": target_score,
        "deadline": deadline_str,
        "days_remaining": sisa_hari,
        "lkps_percent": lkpsPercent,
        "led_percent": ledPercent,
        "evidence_percent": dok_Percent,
    }


def _get_readiness_status(
    lkps_percent: int, led_percent: int, simulation_score: float
) -> str:
    if lkps_percent >= 80 and led_percent >= 80 and simulation_score >= 80:
        return "green"
    if lkps_percent >= 50 and led_percent >= 50 and simulation_score >= 50:
        return "yellow"
    return "red"


def get_dashboard_multiprodi_data(db: Session, tahun: int | None = None):
    list_prodi = db.query(ProgramStudi).all()
    if not list_prodi:
        return {
            "fakultas_summary": {
                "total_prodi": 0,
                "prodi_green": 0,
                "prodi_yellow": 0,
                "prodi_red": 0,
                "avg_lkps_percent": 0.0,
                "avg_led_percent": 0.0,
                "avg_simulation_score": 0.0,
            },
            "prodi_list": [],
            "current_year": tahun or 0,
            "available_years": [],
        }

    # Jika tahun tidak diberikan (initial load), cari tahun terbaru dari semua target
    if not tahun:
        latest_target = (
            db.query(TargetAkreditasi)
            .order_by(TargetAkreditasi.tahun_akreditasi.desc())
            .first()
        )
        if latest_target:
            tahun = latest_target.tahun_akreditasi
        else:
            tahun = date.today().year

    prodi_data_list = []
    for prodi in list_prodi:
        try:
            data = get_dashboard_prodi_data(db, prodi.id, tahun=tahun)
            prodi_data_list.append(data)
        except Exception as e:
            print(f"Error getting data for prodi {prodi.id}: {e}")
            import traceback

            traceback.print_exc()
            continue

    if not prodi_data_list:
        return {
            "fakultas_summary": {
                "total_prodi": 0,
                "prodi_green": 0,
                "prodi_yellow": 0,
                "prodi_red": 0,
                "avg_lkps_percent": 0.0,
                "avg_led_percent": 0.0,
                "avg_simulation_score": 0.0,
            },
            "prodi_list": [],
            "current_year": tahun or 0,
            "available_years": [],
        }

    prodi_summary_list = []
    available_years_set = set()
    current_years = []

    for prodi, p in zip(list_prodi[: len(prodi_data_list)], prodi_data_list):
        profile = p["program_studi_profile"]
        lkps_percent = p.get("lkps_percent", 0)
        led_percent = p.get("led_percent", 0)
        evidence_percent = p.get("evidence_percent", 0)
        simulation_score = float(p.get("score_value", 0))
        target_score = float(p.get("target_score", 0))

        readiness_status = _get_readiness_status(
            lkps_percent, led_percent, simulation_score
        )

        prodi_summary_list.append(
            {
                "id": str(prodi.id),
                "name": profile.get("name", ""),
                "degree": profile.get("degree", ""),
                "accreditation_status": profile.get("last_accreditation_status", ""),
                "accreditation_year": profile.get("last_accreditation_year", 0),
                "lkps_percent": lkps_percent,
                "led_percent": led_percent,
                "evidence_percent": evidence_percent,
                "simulation_score": simulation_score,
                "target_score": target_score,
                "readiness_status": readiness_status,
                "is_active": profile.get("is_active_accreditation", False),
                "days_remaining": p.get("days_remaining", None),
                "prodi_status": profile.get("prodi_status", "aktif"),
            }
        )

        # Kumpulkan semua tahun dari semua target (termasuk is_aktif=False)
        # agar dropdown multiprodi tidak menghilang meski semua prodi dinonaktifkan di tahun tersebut
        all_prodi_targets = (
            db.query(TargetAkreditasi)
            .filter(TargetAkreditasi.program_studi_id == prodi.id)
            .all()
        )
        available_years_set.update(
            t.tahun_akreditasi for t in all_prodi_targets if t.tahun_akreditasi
        )
        current_years.append(p.get("current_year", 0))


    total_prodi = len(prodi_summary_list)
    green_count = sum(1 for p in prodi_summary_list if p["readiness_status"] == "green")
    yellow_count = sum(
        1 for p in prodi_summary_list if p["readiness_status"] == "yellow"
    )
    red_count = sum(1 for p in prodi_summary_list if p["readiness_status"] == "red")

    avg_lkps = (
        float(sum(p["lkps_percent"] for p in prodi_summary_list) / total_prodi)
        if total_prodi > 0
        else 0.0
    )
    avg_led = (
        float(sum(p["led_percent"] for p in prodi_summary_list) / total_prodi)
        if total_prodi > 0
        else 0.0
    )
    avg_simul = (
        float(sum(p["simulation_score"] for p in prodi_summary_list) / total_prodi)
        if total_prodi > 0
        else 0.0
    )

    return {
        "fakultas_summary": {
            "total_prodi": total_prodi,
            "prodi_green": green_count,
            "prodi_yellow": yellow_count,
            "prodi_red": red_count,
            "avg_lkps_percent": avg_lkps,
            "avg_led_percent": avg_led,
            "avg_simulation_score": avg_simul,
        },
        "prodi_list": prodi_summary_list,
        "current_year": tahun or max(current_years) if current_years else 0,
        "available_years": sorted(available_years_set),
    }

def toggle_target_akreditasi(db: Session, prodi_id: UUID, tahun: int, is_aktif: bool) -> dict:
    target = db.query(TargetAkreditasi).filter(
        TargetAkreditasi.program_studi_id == prodi_id,
        TargetAkreditasi.tahun_akreditasi == tahun
    ).first()

    if is_aktif:
        if not target:
            target = TargetAkreditasi(
                program_studi_id=prodi_id,
                tahun_akreditasi=tahun,
                target_skor=None,
                deadline=None,
                is_aktif=True
            )
            db.add(target)
        else:
            target.is_aktif = True
    else:
        if target:
            target.is_aktif = False
    
    db.commit()
    return {"message": "Success"}
