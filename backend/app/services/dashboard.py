from datetime import date
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi
from app.models.kriteria import Kriteria
from app.models.indikator import Indikator
from app.models.data_lkps import DataLKPS
from app.models.narasi_led import NarasiLED
from app.models.evidence import Evidence, EvidenceIndikator


def get_dashboard_prodi_data(db: Session, prodi_id: UUID) -> dict:
    prodi = db.query(ProgramStudi).filter(ProgramStudi.id == prodi_id).first()
    if not prodi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program Studi tidak ditemukan."
        )

    active_target = db.query(TargetAkreditasi)\
        .filter(TargetAkreditasi.program_studi_id == prodi_id, TargetAkreditasi.is_aktif == True)\
        .first()

    aktif_akreditasi = active_target is not None

    target_score = active_target.target_skor if active_target and active_target.target_skor else 3.5
    deadline_str = active_target.deadline.strftime("%d %B %Y") if active_target and active_target.deadline else "Belum Diatur"
    
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
                # Check LKPS
                lkps_count = db.query(DataLKPS).filter(
                    DataLKPS.target_akreditasi_id == active_target.id,
                    DataLKPS.indikator_id.in_(ind_ids)
                ).count()
                lkps_ada = lkps_count > 0

                # Check Evidence via junction table
                evid_count = db.query(EvidenceIndikator).filter(
                    EvidenceIndikator.indikator_id.in_(ind_ids),
                    EvidenceIndikator.target_akreditasi_id == active_target.id
                ).count()
                has_evidence = evid_count > 0

                # Check LED
                led_count = db.query(NarasiLED).filter(
                    NarasiLED.target_akreditasi_id == active_target.id,
                    NarasiLED.indikator_id.in_(ind_ids)
                ).count()
                led_ada = led_count > 0

        # TODO Replace statis 50/100 dengan rumus perhitungan progres indikator IABEE aktual
        progres_mock = 50 if lkps_ada or led_ada else 0
        if lkps_ada and led_ada: progres_mock = 100

        # TODO Status & Label saat ini hanya membaca mentah dari progres_mock di atas
        k_status = "green" if progres_mock >= 80 else ("yellow" if progres_mock >= 50 else "red")
        k_status_label = "Baik" if progres_mock >= 80 else ("Cukup" if progres_mock >= 50 else "Buruk")

        has_formula = any(ind.tipe_input == "formula" for ind in indikators)
        has_manual = any(ind.tipe_input == "manual" for ind in indikators)
        
        if has_formula and has_manual:
            c_input_type = "both"
        elif has_formula:
            c_input_type = "formula"
        elif has_manual:
            c_input_type = "manual"
        else:
            c_input_type = "both"

        kriteria_list_response.append({
            "id": k.kode.lower(),
            "name": f"{k.nama} ({k.kode})",
            "status": k_status,
            "status_label": k_status_label,
            "progress": progres_mock,
            "has_lkps": True, 
            "lkps_available": lkps_ada,
            "has_led": True,
            "led_available": led_ada,
            "has_evidence": has_evidence,
            "input_type": c_input_type
        })


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
            early_warnings.append("Deadline akreditasi telah lewat atau berakhir hari ini!")

    if not aktif_akreditasi:
        pesan_rekomendasi.append("Siklus akreditasi belum aktif. Hubungi Koordinator untuk mengaktifkan siklus baru.")
    else:
        # Check criteria completeness
        for k_resp in kriteria_list_response:
            if k_resp["progress"] < 100:
                kr_name = k_resp["name"].split(" ")[-1].strip("()")
                # Give specific recommendation based on which doc is missing
                if not k_resp["lkps_available"] and not k_resp["led_available"]:
                    pesan_rekomendasi.append(f"Segera unggah data LKPS dan rumuskan Narasi LED pada kriteria {kr_name}.")
                elif not k_resp["lkps_available"]:
                    pesan_rekomendasi.append(f"Data LKPS belum lengkap untuk kriteria {kr_name}.")
                elif not k_resp["led_available"]:
                    pesan_rekomendasi.append(f"Narasi kualitatif LED belum selesai pada kriteria {kr_name}.")


    # 5. Calculate overall progress percentages
    total_criteria = len(kriteria_list_response) if kriteria_list_response else 1
    lkps_completed_count = sum(1 for k in kriteria_list_response if k["lkps_available"])
    led_completed_count = sum(1 for k in kriteria_list_response if k["led_available"])
    evidence_completed_count = sum(1 for k in kriteria_list_response if k["has_evidence"])
    
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
            "last_accreditation_year": prodi.tanggal_akreditasi.year if prodi.tanggal_akreditasi else 0,
            "is_active_accreditation": aktif_akreditasi
        },
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
        "evidence_percent": dok_Percent
    }
