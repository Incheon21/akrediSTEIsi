from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi
from app.schemas.target_akreditasi import SetTargetScoreRequest, SetDeadlineRequest, SetNotifikasiRequest, TargetAkreditasiResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/target_akreditasi", tags=["target_akreditasi"])

@router.post(
    "/score",
    response_model=TargetAkreditasiResponse,
    summary="Set target score for a program studi",
)
def set_target_score(
    body: SetTargetScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    prodi_exists = db.execute(
        select(ProgramStudi.status)
        .where(ProgramStudi.id == body.prodi_id)
    ).first()

    if not prodi_exists:
        raise HTTPException(status_code = 404, detail="Prodi not found")

    target = db.execute(
        select(TargetAkreditasi)
        .where(TargetAkreditasi.program_studi_id == body.prodi_id,
               TargetAkreditasi.tahun_akreditasi == body.tahun_akreditasi)
    ).scalars().first()
    
    if not target:
        raise HTTPException(status_code = 422, detail="Prodi not active in that year")
    
    target.target_skor = body.target_skor
    db.flush()
    db.commit()
    return TargetAkreditasiResponse.model_validate(target)

@router.post(
    "/deadline",
    response_model=TargetAkreditasiResponse,
    summary="Set deadline for a program studi",
)
def set_deadline(
    body: SetDeadlineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    prodi_exists = db.execute(
        select(ProgramStudi.status)
        .where(ProgramStudi.id == body.prodi_id)
    ).first()

    if not prodi_exists:
        raise HTTPException(status_code = 404, detail="Prodi not found")

    target = db.execute(
        select(TargetAkreditasi)
        .where(TargetAkreditasi.program_studi_id == body.prodi_id,
               TargetAkreditasi.tahun_akreditasi == body.tahun_akreditasi)
    ).scalars().first()
    
    if not target:
        raise HTTPException(status_code = 422, detail="Prodi not active in that year")
    
    target.deadline = body.deadline
    db.flush()
    db.commit()
    return TargetAkreditasiResponse.model_validate(target)


@router.get(
    "/status",
    summary="Get notifikasi_aktif status for the active target of a prodi",
)
def get_notifikasi_status(
    prodi_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    target = db.execute(
        select(TargetAkreditasi)
        .where(
            TargetAkreditasi.program_studi_id == prodi_id,
            TargetAkreditasi.is_aktif.is_(True),
        )
    ).scalars().first()

    if not target:
        return {"notifikasi_aktif": False, "has_target": False}

    return {
        "notifikasi_aktif": bool(target.notifikasi_aktif),
        "has_target": True,
        "tahun_akreditasi": target.tahun_akreditasi,
    }


@router.post(
    "/notifikasi",
    response_model=TargetAkreditasiResponse,
    summary="Toggle notifikasi deadline for a program studi target",
)
def set_notifikasi(
    body: SetNotifikasiRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    target = db.execute(
        select(TargetAkreditasi)
        .where(
            TargetAkreditasi.program_studi_id == body.prodi_id,
            TargetAkreditasi.tahun_akreditasi == body.tahun_akreditasi,
        )
    ).scalars().first()

    if not target:
        raise HTTPException(status_code=422, detail="Target akreditasi tidak ditemukan")

    target.notifikasi_aktif = body.notifikasi_aktif
    db.flush()
    db.commit()
    return TargetAkreditasiResponse.model_validate(target)
