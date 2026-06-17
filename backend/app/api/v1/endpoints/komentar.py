from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.models.komentar import Komentar
from app.models.target_akreditasi import TargetAkreditasi
from app.schemas.komentar import KomentarCreate, KomentarResponse, KomentarUpdate
from app.utils.dependencies import get_current_user, require_role
from app.services.notifikasi import notify_komentar_to_tim_prodi

router = APIRouter(prefix="/target/{target_id}/komentar", tags=["komentar"])


@router.get("/", response_model=List[KomentarResponse])
def get_komentar_list(
    target_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = db.query(TargetAkreditasi).filter(TargetAkreditasi.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target akreditasi tidak ditemukan")

    komentar_list = (
        db.query(Komentar)
        .options(joinedload(Komentar.user))
        .filter(Komentar.target_akreditasi_id == target_id)
        .order_by(Komentar.created_at.asc())
        .all()
    )

    result = []
    for k in komentar_list:
        user_info = None
        if k.user:
            user_info = {
                "id": k.user.id,
                "nama": k.user.nama,
                "role": k.user.role.name if k.user.role else "unknown",
            }
        result.append(
            KomentarResponse(
                id=k.id,
                target_akreditasi_id=k.target_akreditasi_id,
                user_id=k.user_id,
                isi_komentar=k.isi_komentar,
                created_at=k.created_at,
                updated_at=k.updated_at,
                user=user_info,
            )
        )
    return result


@router.post("/", response_model=KomentarResponse, status_code=status.HTTP_201_CREATED)
def create_komentar(
    target_id: UUID,
    payload: KomentarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("pimpinan", "admin")),
):
    target = db.query(TargetAkreditasi).filter(TargetAkreditasi.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target akreditasi tidak ditemukan")

    try:
        new_komentar = Komentar(
            target_akreditasi_id=target_id,
            user_id=current_user.id,
            isi_komentar=payload.isi_komentar,
        )
        db.add(new_komentar)
        db.commit()
        db.refresh(new_komentar)

        notify_komentar_to_tim_prodi(
            db,
            komentar_id=new_komentar.id,
            target_akreditasi_id=target_id,
            pengirim_nama=current_user.nama,
            isi_komentar=payload.isi_komentar,
            program_studi_id=target.program_studi_id,
        )

        user_info = {
            "id": current_user.id,
            "nama": current_user.nama,
            "role": current_user.role.name if current_user.role else "unknown",
        }
        return KomentarResponse(
            id=new_komentar.id,
            target_akreditasi_id=new_komentar.target_akreditasi_id,
            user_id=new_komentar.user_id,
            isi_komentar=new_komentar.isi_komentar,
            created_at=new_komentar.created_at,
            updated_at=new_komentar.updated_at,
            user=user_info,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan komentar: {str(e)}")


@router.put("/{komentar_id}", response_model=KomentarResponse)
def update_komentar(
    target_id: UUID,
    komentar_id: UUID,
    payload: KomentarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("pimpinan", "admin")),
):
    komentar = (
        db.query(Komentar)
        .options(joinedload(Komentar.user))
        .filter(Komentar.id == komentar_id, Komentar.target_akreditasi_id == target_id)
        .first()
    )
    if not komentar:
        raise HTTPException(status_code=404, detail="Komentar tidak ditemukan")

    if str(komentar.user_id) != str(current_user.id) and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Hanya penulis komentar yang dapat mengedit")

    try:
        komentar.isi_komentar = payload.isi_komentar
        db.commit()
        db.refresh(komentar)

        user_info = None
        if komentar.user:
            user_info = {
                "id": komentar.user.id,
                "nama": komentar.user.nama,
                "role": komentar.user.role.name if komentar.user.role else "unknown",
            }
        return KomentarResponse(
            id=komentar.id,
            target_akreditasi_id=komentar.target_akreditasi_id,
            user_id=komentar.user_id,
            isi_komentar=komentar.isi_komentar,
            created_at=komentar.created_at,
            updated_at=komentar.updated_at,
            user=user_info,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal mengedit komentar: {str(e)}")


@router.delete("/{komentar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_komentar(
    target_id: UUID,
    komentar_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("pimpinan", "admin")),
):
    komentar = (
        db.query(Komentar)
        .filter(Komentar.id == komentar_id, Komentar.target_akreditasi_id == target_id)
        .first()
    )
    if not komentar:
        raise HTTPException(status_code=404, detail="Komentar tidak ditemukan")

    if str(komentar.user_id) != str(current_user.id) and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Hanya penulis komentar yang dapat menghapus")

    try:
        db.delete(komentar)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menghapus komentar: {str(e)}")
