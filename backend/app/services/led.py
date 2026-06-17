from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.indikator import Indikator
from app.models.narasi_led import NarasiLED
from app.models.target_akreditasi import TargetAkreditasi
from app.models.user import User


def _validate_target_akreditasi_for_user(
    db: Session,
    target_akreditasi_id: UUID,
    current_user: User,
) -> TargetAkreditasi:
    """
    Validate that target akreditasi exists and can be accessed by current user.
    tim_prodi can only access their own program studi target.
    """
    target = (
        db.query(TargetAkreditasi)
        .filter(TargetAkreditasi.id == target_akreditasi_id)
        .first()
    )
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target akreditasi tidak ditemukan.",
        )

    # Restrict tim_prodi to their own prodi
    role_name = current_user.role.name if current_user.role else None
    if role_name == "tim_prodi":
        if current_user.program_studi_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun tim prodi tidak memiliki program studi terasosiasi.",
            )
        if target.program_studi_id != current_user.program_studi_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki akses ke target akreditasi ini.",
            )

    return target


def _validate_indikator_exists(db: Session, indikator_id: UUID) -> Indikator:
    indikator = db.query(Indikator).filter(Indikator.id == indikator_id).first()
    if indikator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indikator tidak ditemukan.",
        )
    return indikator


def _validate_narasi_content(narasi: str) -> str:
    """
    Enforce business rule from use case:
    narasi LED cannot be empty.
    """
    cleaned = (narasi or "").strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Narasi LED tidak boleh kosong.",
        )
    return cleaned


def upsert_led_narasi(
    db: Session,
    *,
    target_akreditasi_id: UUID,
    indikator_id: UUID,
    narasi: str,
    current_user: User,
) -> NarasiLED:
    """
    Create or update narasi LED by (target_akreditasi_id, indikator_id).

    Handles potential race conditions when concurrent requests insert the same
    target+indikator pair by recovering from unique-constraint conflicts.
    """
    _validate_target_akreditasi_for_user(
        db=db,
        target_akreditasi_id=target_akreditasi_id,
        current_user=current_user,
    )
    _validate_indikator_exists(db=db, indikator_id=indikator_id)
    cleaned_narasi = _validate_narasi_content(narasi)

    existing = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target_akreditasi_id,
            NarasiLED.indikator_id == indikator_id,
        )
        .first()
    )

    if existing:
        existing.narasi = cleaned_narasi
        db.add(existing)
        try:
            db.commit()
            db.refresh(existing)
            return existing
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Konflik data saat menyimpan narasi LED. Silakan coba lagi.",
            )
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Terjadi kesalahan database saat menyimpan narasi LED.",
            )

    new_row = NarasiLED(
        target_akreditasi_id=target_akreditasi_id,
        indikator_id=indikator_id,
        narasi=cleaned_narasi,
    )
    db.add(new_row)

    try:
        db.commit()
        db.refresh(new_row)
        return new_row
    except IntegrityError:
        db.rollback()

        # Likely a race on unique(target_akreditasi_id, indikator_id):
        # fetch row created by concurrent transaction, then update it.
        raced = (
            db.query(NarasiLED)
            .filter(
                NarasiLED.target_akreditasi_id == target_akreditasi_id,
                NarasiLED.indikator_id == indikator_id,
            )
            .first()
        )

        if raced is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Konflik data saat menyimpan narasi LED. Silakan coba lagi.",
            )

        raced.narasi = cleaned_narasi
        db.add(raced)
        try:
            db.commit()
            db.refresh(raced)
            return raced
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Terjadi kesalahan database saat menyimpan narasi LED.",
            )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan database saat menyimpan narasi LED.",
        )


def get_led_narasi_batch(
    db: Session,
    *,
    target_akreditasi_id: UUID,
    indikator_ids: list[UUID],
    current_user: User,
) -> dict[str, NarasiLED]:
    """
    Fetch all existing narasi LED for a target + list of indikator IDs in one query.
    Returns a dict keyed by indikator_id (str). Missing entries are simply absent.
    """
    _validate_target_akreditasi_for_user(
        db=db,
        target_akreditasi_id=target_akreditasi_id,
        current_user=current_user,
    )

    rows = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target_akreditasi_id,
            NarasiLED.indikator_id.in_(indikator_ids),
        )
        .all()
    )

    return {str(row.indikator_id): row for row in rows}


def get_led_narasi(
    db: Session,
    *,
    target_akreditasi_id: UUID,
    indikator_id: UUID,
    current_user: User,
) -> NarasiLED:
    """
    Get narasi LED by target and indikator.
    """
    _validate_target_akreditasi_for_user(
        db=db,
        target_akreditasi_id=target_akreditasi_id,
        current_user=current_user,
    )
    _validate_indikator_exists(db=db, indikator_id=indikator_id)

    item = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target_akreditasi_id,
            NarasiLED.indikator_id == indikator_id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narasi LED belum tersedia untuk indikator ini.",
        )

    return item
