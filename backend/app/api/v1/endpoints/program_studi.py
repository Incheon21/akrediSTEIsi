"""Program Studi endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.program_studi import ProgramStudi
from app.schemas.program_studi import ProgramStudiResponse, ProgramStudiUpdate

router = APIRouter(prefix="/program-studi", tags=["program-studi"])


@router.get("", response_model=list[ProgramStudiResponse])
def list_program_studi(db: Session = Depends(get_db)):
    rows = db.execute(select(ProgramStudi).order_by(ProgramStudi.nama)).scalars().all()
    return rows


@router.get("/{program_studi_id}", response_model=ProgramStudiResponse)
def get_program_studi(program_studi_id: UUID, db: Session = Depends(get_db)):
    ps = db.get(ProgramStudi, program_studi_id)
    if not ps:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program studi tidak ditemukan")
    return ps


@router.put("/{program_studi_id}", response_model=ProgramStudiResponse)
def update_program_studi(
    program_studi_id: UUID,
    body: ProgramStudiUpdate,
    db: Session = Depends(get_db),
):
    ps = db.get(ProgramStudi, program_studi_id)
    if not ps:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program studi tidak ditemukan")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(ps, field, value)
    db.commit()
    db.refresh(ps)
    return ps
