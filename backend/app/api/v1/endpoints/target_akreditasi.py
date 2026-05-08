from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi
from app.schemas.target_akreditasi import SetTargetScoreRequest, SetDeadlineRequest, TargetAkreditasiResponse
from app.services.dashboard import get_dashboard_prodi_data
from app.services.dashboard import get_dashboard_prodi_data
from app.utils.dependencies import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/target_akreditasi", tags=["target_akreditasi"])

@router.post(
    "/score",
    response_model=TargetAkreditasiResponse,
    summary="Set target score for a program studi",
    dependencies=[Depends(require_role("admin", "koordinator", "pimpinan"))]
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
    dependencies=[Depends(require_role("admin", "koordinator", "pimpinan"))]
)
def set_target_score(
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
