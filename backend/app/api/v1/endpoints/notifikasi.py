from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.notifikasi import Notifikasi
from app.models.user import User
from app.services.notifikasi import sync_generated_notifications
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/notifikasi", tags=["notifikasi"])


class NotifikasiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kategori: str
    severity: str
    judul: str
    pesan: str
    href: str | None = None
    is_read: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class NotifikasiListResponse(BaseModel):
    unread_count: int
    items: list[NotifikasiResponse]


@router.get("", response_model=NotifikasiListResponse)
def list_notifikasi(
    limit: int = 20,
    program_studi_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sync_generated_notifications(db, current_user)

    from app.models.target_akreditasi import TargetAkreditasi
    from sqlalchemy import or_

    query = db.query(Notifikasi).outerjoin(
        TargetAkreditasi, Notifikasi.target_akreditasi_id == TargetAkreditasi.id
    ).filter(
        Notifikasi.user_id == current_user.id,
        or_(TargetAkreditasi.id.is_(None), TargetAkreditasi.notifikasi_aktif.is_(True))
    )
    if program_studi_id:
        query = query.filter(Notifikasi.program_studi_id == program_studi_id)

    unread_count = query.filter(Notifikasi.is_read.is_(False)).count()
    items = (
        query.order_by(Notifikasi.is_read.asc(), Notifikasi.updated_at.desc())
        .limit(limit)
        .all()
    )

    return {"unread_count": unread_count, "items": items}


@router.post("/{notifikasi_id}/read", response_model=NotifikasiResponse)
def mark_notifikasi_read(
    notifikasi_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Notifikasi)
        .filter(Notifikasi.id == notifikasi_id, Notifikasi.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notifikasi tidak ditemukan.",
        )

    row.is_read = True
    row.read_at = datetime.now()
    db.commit()
    db.refresh(row)
    return row


@router.post("/read-all")
def mark_all_notifikasi_read(
    program_studi_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now()
    from app.models.target_akreditasi import TargetAkreditasi
    from sqlalchemy import or_

    query = db.query(Notifikasi).outerjoin(
        TargetAkreditasi, Notifikasi.target_akreditasi_id == TargetAkreditasi.id
    ).filter(
        Notifikasi.user_id == current_user.id,
        Notifikasi.is_read.is_(False),
        or_(TargetAkreditasi.id.is_(None), TargetAkreditasi.notifikasi_aktif.is_(True))
    )
    if program_studi_id:
        query = query.filter(Notifikasi.program_studi_id == program_studi_id)

    rows = query.all()
    for row in rows:
        row.is_read = True
        row.read_at = now

    db.commit()
    return {"marked_read": len(rows)}
