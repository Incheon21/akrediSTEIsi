"""Program Studi endpoints – read-only list used by the LKPS submission form."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.program_studi import ProgramStudi

router = APIRouter(prefix="/program-studi", tags=["program-studi"])


@router.get("")
def list_program_studi(db: Session = Depends(get_db)):
    rows = db.execute(
        select(ProgramStudi).order_by(ProgramStudi.nama)
    ).scalars().all()
    return [
        {
            "id": str(ps.id),
            "kode": ps.kode,
            "nama": ps.nama,
            "jenjang": ps.jenjang,
            "fakultas": ps.fakultas,
            "perguruan_tinggi": ps.perguruan_tinggi,
            "akreditasi": ps.akreditasi,
            "status": ps.status,
        }
        for ps in rows
    ]
