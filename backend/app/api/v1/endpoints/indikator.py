from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/indikator", tags=["indikator"])


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


@router.get("/progress/status")
def get_indikator_progress_status(
    target_akreditasi_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mendapatkan data status progres pengisian indikator prodi (T-46).
    Mengembalikan persentase penyelesaian untuk masing-masing indikator agar
    frontend dapat me-render progress bar.
    """
    # Mengambil semua indikator
    indikators = db.query(Indikator).all()

    progress_data = []
    completed_count = 0

    for ind in indikators:
        # TODO: Integrasi dengan logic T-45 (Alvin) untuk kalkulasi spesifik per indikator.
        # Saat ini kita set default placeholder.
        is_complete = False
        pct = 100 if is_complete else 0

        if is_complete:
            completed_count += 1

        progress_data.append(
            {
                "indikator_id": ind.id,
                "kode_indikator": ind.kode_indikator,
                "kriteria_id": ind.kriteria_id,
                "tipe_input": ind.tipe_input,
                "completion_percentage": pct,
                "is_complete": is_complete,
            }
        )

    overall_pct = (completed_count / len(indikators) * 100) if indikators else 0.0

    return {
        "total_indicators": len(indikators),
        "completed_indicators": completed_count,
        "overall_progress_percentage": round(overall_pct, 2),
        "indicators": progress_data,
    }
