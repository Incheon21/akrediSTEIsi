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
