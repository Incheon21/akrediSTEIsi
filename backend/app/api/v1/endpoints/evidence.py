import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.evidence import EvidenceResponse
from app.services.evidence import (
    delete_evidence,
    get_evidence_by_id,
    get_evidence_list,
    get_physical_file_path,
    upload_evidence,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post(
    "/",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new evidence document",
)
def upload_evidence_endpoint(
    file: UploadFile = File(...),
    judul: str = Form(...),
    deskripsi: Optional[str] = Form(None),
    is_global: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an evidence file.
    Accepts form data for metadata and the file itself.
    """
    return upload_evidence(
        db=db,
        file=file,
        judul=judul,
        deskripsi=deskripsi,
        is_global=is_global,
        uploaded_by=current_user.id,
        program_studi_id=current_user.program_studi_id,
    )


@router.get(
    "/",
    response_model=List[EvidenceResponse],
    summary="List all evidence documents",
)
def read_evidence_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a list of evidence metadata.
    Filters by the current user's prodi (shows global + prodi-specific evidence).
    Admins and pimpinan (no prodi) see all evidence.
    """
    return get_evidence_list(
        db=db,
        skip=skip,
        limit=limit,
        program_studi_id=current_user.program_studi_id,
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
    summary="Get evidence metadata by ID",
)
def read_evidence(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve metadata for a specific evidence document.
    """
    evidence = get_evidence_by_id(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )
    return evidence


@router.get(
    "/{evidence_id}/download",
    summary="Download the physical evidence file",
)
def download_evidence(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download the actual physical file associated with the evidence record.
    """
    evidence = get_evidence_by_id(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )

    file_path = get_physical_file_path(evidence.url_file)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical file not found on the server",
        )

    # Clean the judul to be used as a filename
    safe_judul = "".join(
        [c for c in evidence.judul if c.isalpha() or c.isdigit() or c in " -_"]
    ).strip()
    download_filename = f"{safe_judul}{file_path.suffix}"

    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type=evidence.tipe_file or "application/octet-stream",
    )


@router.delete(
    "/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an evidence document",
)
def delete_evidence_endpoint(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an evidence record and its associated physical file.
    """
    evidence = get_evidence_by_id(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )

    # In a real app, you might want to check if the current_user is the uploader or an admin
    # if evidence.uploaded_by != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_evidence(db=db, evidence_id=evidence_id)
