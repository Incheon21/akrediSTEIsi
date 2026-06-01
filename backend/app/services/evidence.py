import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.evidence import Evidence, EvidenceIndikator, EvidenceProdi

# Define storage directory path relative to the backend root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "evidence"

# Allowed file extensions for accreditation evidence
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".jpeg", ".jpg", ".png"}


def ensure_storage_dir_exists():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return ext


def upload_evidence(
    db: Session,
    file: UploadFile,
    judul: str,
    deskripsi: Optional[str] = None,
    is_global: bool = False,
    uploaded_by: Optional[uuid.UUID] = None,
    program_studi_id: Optional[uuid.UUID] = None,
) -> Evidence:
    """
    Handles saving the file to local disk and creating the database record.
    When is_global=False and program_studi_id is provided, auto-links the evidence
    to that specific prodi via the EvidenceProdi junction table.
    """
    ensure_storage_dir_exists()

    # Validate file type
    if file.filename:
        ext = validate_file_extension(file.filename)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a filename."
        )

    # Generate unique filename to prevent path traversal and collisions
    file_uuid = str(uuid.uuid4())
    stored_filename = f"{file_uuid}{ext}"
    file_path = STORAGE_DIR / stored_filename

    # Save physical file to storage
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file to disk: {str(e)}",
        )
    finally:
        file.file.close()

    # Relative URL path to be stored in DB (can be adjusted based on how we serve static files)
    url_file = f"/storage/evidence/{stored_filename}"

    # Create DB record
    db_evidence = Evidence(
        id=uuid.UUID(file_uuid),
        judul=judul,
        deskripsi=deskripsi,
        url_file=url_file,
        tipe_file=file.content_type,
        is_global=is_global,
        uploaded_by=uploaded_by,
    )

    db.add(db_evidence)
    db.flush()  # flush so db_evidence.id is available for junction table

    # Auto-link to prodi when not global
    if not is_global and program_studi_id:
        db.add(
            EvidenceProdi(
                evidence_id=db_evidence.id,
                prodi_id=program_studi_id,
            )
        )

    db.commit()
    db.refresh(db_evidence)

    return db_evidence


def get_evidence_by_id(db: Session, evidence_id: uuid.UUID) -> Optional[Evidence]:
    """Retrieve an evidence record by ID."""
    return db.query(Evidence).filter(Evidence.id == evidence_id).first()


def get_evidence_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    program_studi_id: Optional[uuid.UUID] = None,
) -> List[Evidence]:
    """
    Retrieve a list of evidence records.
    If program_studi_id is provided, returns:
      - All global evidence (is_global=True)
      - Plus evidence linked to that specific prodi via EvidenceProdi
    If no program_studi_id, returns all evidence (admin view).
    """
    if program_studi_id:
        from sqlalchemy import or_

        linked_ids = (
            db.query(EvidenceProdi.evidence_id)
            .filter(EvidenceProdi.prodi_id == program_studi_id)
            .subquery()
        )
        return (
            db.query(Evidence)
            .filter(
                or_(
                    Evidence.is_global == True,
                    Evidence.id.in_(linked_ids),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    return db.query(Evidence).offset(skip).limit(limit).all()


def delete_evidence(db: Session, evidence_id: uuid.UUID) -> bool:
    """
    Deletes the evidence database record and removes the physical file from disk.
    """
    db_evidence = get_evidence_by_id(db, evidence_id)
    if not db_evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )

    # Extract filename from url_file to delete physical file
    filename = Path(db_evidence.url_file).name
    file_path = STORAGE_DIR / filename

    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Optionally log the error, but proceed to delete the DB record anyway
            print(f"Failed to delete physical file {file_path}: {e}")

    # Delete DB record
    db.delete(db_evidence)
    db.commit()

    return True


def get_physical_file_path(url_file: str) -> Path:
    """Helper to resolve the physical path for downloading/serving."""
    filename = Path(url_file).name
    return STORAGE_DIR / filename


def link_evidence_indikator(
    db: Session,
    evidence_id: uuid.UUID,
    indikator_id: uuid.UUID,
    target_akreditasi_id: uuid.UUID,
) -> EvidenceIndikator:
    """
    Create a link between an evidence record and an indikator for a given
    target_akreditasi. Raises 409 if the link already exists.
    """
    existing = (
        db.query(EvidenceIndikator)
        .filter(
            EvidenceIndikator.evidence_id == evidence_id,
            EvidenceIndikator.indikator_id == indikator_id,
            EvidenceIndikator.target_akreditasi_id == target_akreditasi_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Link between this evidence and indikator already exists.",
        )

    link = EvidenceIndikator(
        evidence_id=evidence_id,
        indikator_id=indikator_id,
        target_akreditasi_id=target_akreditasi_id,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_evidence_indikator_links(
    db: Session,
    evidence_id: uuid.UUID,
) -> List[EvidenceIndikator]:
    """Return all EvidenceIndikator links for a given evidence record."""
    return (
        db.query(EvidenceIndikator)
        .filter(EvidenceIndikator.evidence_id == evidence_id)
        .all()
    )


def unlink_evidence_indikator(
    db: Session,
    evidence_id: uuid.UUID,
    indikator_id: uuid.UUID,
    target_akreditasi_id: uuid.UUID,
) -> bool:
    """
    Remove the link between an evidence record and an indikator.
    Raises 404 if the link does not exist.
    """
    link = (
        db.query(EvidenceIndikator)
        .filter(
            EvidenceIndikator.evidence_id == evidence_id,
            EvidenceIndikator.indikator_id == indikator_id,
            EvidenceIndikator.target_akreditasi_id == target_akreditasi_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EvidenceIndikator link not found.",
        )

    db.delete(link)
    db.commit()
    return True
