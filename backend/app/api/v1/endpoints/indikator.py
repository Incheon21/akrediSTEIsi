from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.lkps import LkpsSubmission
from app.models.narasi_led import NarasiLED
from app.models.target_akreditasi import TargetAkreditasi
from app.models.user import User
from app.services.dashboard import KRITERIA_LKPS_MODELS
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/indikator", tags=["indikator"])


# NOTE: Static routes MUST be declared before parameterised routes.
# /progress/status must come before /{indikator_id} or FastAPI will try to
# parse the literal string "progress" as a UUID and return a 422.


@router.get("/progress/status")
def get_indikator_progress_status(
    target_akreditasi_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mendapatkan data status progres pengisian indikator prodi (T-46).
    Mengembalikan persentase penyelesaian untuk masing-masing indikator agar
    frontend dapat me-render progress bar.

    Uses real completion logic:
    - LED / narasi indicators: complete when NarasiLED has been filled.
    - LKPS indicators: uses per-kriteria LKPS section fill rate (same logic
      as the dashboard service, sourced from KRITERIA_LKPS_MODELS).
    """
    # 1. Validate target akreditasi
    target = (
        db.query(TargetAkreditasi)
        .filter(TargetAkreditasi.id == target_akreditasi_id)
        .first()
    )
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target akreditasi tidak ditemukan.",
        )

    prodi_id = target.program_studi_id

    # 2. Get LKPS submission for this prodi + year so we can check section fill rate
    lkps_submission = (
        db.query(LkpsSubmission)
        .filter(
            LkpsSubmission.program_studi_id == prodi_id,
            LkpsSubmission.tahun_ts == target.tahun_akreditasi,
        )
        .first()
    )

    # 3. Pre-compute LKPS completion percentage per kriteria_id
    #    Reuses KRITERIA_LKPS_MODELS from dashboard service (T-45 logic by Alvin).
    kriteria_lkps_pct: dict[UUID, float] = {}
    all_kriteria = db.query(Kriteria).all()

    for k in all_kriteria:
        models = KRITERIA_LKPS_MODELS.get(k.kode, [])
        if lkps_submission and models:
            sections_with_data = sum(
                1
                for model in models
                if db.query(model)
                .filter(model.submission_id == lkps_submission.id)
                .first()
            )
            kriteria_lkps_pct[k.id] = (sections_with_data / len(models)) * 100
        else:
            kriteria_lkps_pct[k.id] = 0.0

    # 4. Pre-fetch all filled narasi IDs for this target in one query
    filled_narasi_indikator_ids: set[UUID] = set(
        row.indikator_id
        for row in db.query(NarasiLED.indikator_id)
        .filter(
            NarasiLED.target_akreditasi_id == target_akreditasi_id,
            NarasiLED.narasi.isnot(None),
            NarasiLED.narasi != "",
        )
        .all()
    )

    # 5. Build per-indicator progress
    indikators = db.query(Indikator).options(joinedload(Indikator.kriteria)).all()

    progress_data = []
    completed_count = 0

    for ind in indikators:
        if ind.tipe_input in ("narasi", "text"):
            # LED-type indicator: complete when narasi has been saved
            is_complete = ind.id in filled_narasi_indikator_ids
            pct = 100.0 if is_complete else 0.0
        else:
            # LKPS-type indicator: use the kriteria-level LKPS section fill rate
            pct = kriteria_lkps_pct.get(ind.kriteria_id, 0.0)
            is_complete = pct >= 100.0

        if is_complete:
            completed_count += 1

        progress_data.append(
            {
                "indikator_id": ind.id,
                "kode_indikator": ind.kode_indikator,
                "kriteria_id": ind.kriteria_id,
                "tipe_input": ind.tipe_input,
                "completion_percentage": round(pct, 2),
                "is_complete": is_complete,
            }
        )

    overall_pct = (completed_count / len(indikators) * 100) if indikators else 0.0

    return {
        "target_akreditasi_id": target_akreditasi_id,
        "total_indicators": len(indikators),
        "completed_indicators": completed_count,
        "overall_progress_percentage": round(overall_pct, 2),
        "indicators": progress_data,
    }


@router.get("/")
def get_indikators(
    kriteria_kode: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mendapatkan daftar indikator, dengan opsional filter berdasarkan kode kriteria.
    """
    query = db.query(Indikator).options(joinedload(Indikator.kriteria))

    if kriteria_kode:
        query = query.join(Kriteria).filter(Kriteria.kode.ilike(kriteria_kode))

    return query.all()


@router.get("/{indikator_id}")
def get_indikator_by_id(
    indikator_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mendapatkan detail indikator berdasarkan ID.
    Dibutuhkan oleh frontend untuk memuat detail indikator di halaman LED.
    """
    indikator = db.query(Indikator).filter(Indikator.id == indikator_id).first()
    if not indikator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Indikator tidak ditemukan."
        )
    return indikator
