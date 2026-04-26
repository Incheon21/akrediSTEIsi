import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.evidence import EvidenceIndikator
from app.models.user import User
from app.schemas.evidence import (
    EvidenceIndikatorRequest,
    EvidenceIndikatorResponse,
    EvidenceResponse,
)
from app.services.evidence import (
    delete_evidence,
    get_evidence_by_id,
    get_evidence_indikator_links,
    get_evidence_list,
    get_physical_file_path,
    link_evidence_indikator,
    unlink_evidence_indikator,
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

    if current_user.id != evidence.uploaded_by and current_user.role.name not in (
        "admin",
        "koordinator",
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this evidence.",
        )

    delete_evidence(db=db, evidence_id=evidence_id)


@router.post(
    "/{evidence_id}/indikator",
    response_model=EvidenceIndikatorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link an evidence document to an indikator",
)
def add_evidence_indikator(
    evidence_id: uuid.UUID,
    body: EvidenceIndikatorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an EvidenceIndikator record linking the given evidence to an indikator
    for a specific target_akreditasi. Returns 404 if the evidence does not exist,
    409 if the link already exists.
    """
    evidence = get_evidence_by_id(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )

    return link_evidence_indikator(
        db=db,
        evidence_id=evidence_id,
        indikator_id=body.indikator_id,
        target_akreditasi_id=body.target_akreditasi_id,
    )


@router.get(
    "/{evidence_id}/indikator",
    response_model=List[EvidenceIndikatorResponse],
    summary="List all indikator links for an evidence document",
)
def read_evidence_indikator_links(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all EvidenceIndikator records associated with the given evidence.
    Returns 404 if the evidence does not exist.
    """
    evidence = get_evidence_by_id(db=db, evidence_id=evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found"
        )

    return get_evidence_indikator_links(db=db, evidence_id=evidence_id)


@router.delete(
    "/{evidence_id}/indikator/{indikator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an indikator link from an evidence document",
)
def remove_evidence_indikator(
    evidence_id: uuid.UUID,
    indikator_id: uuid.UUID,
    target_akreditasi_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete the EvidenceIndikator link identified by evidence_id, indikator_id,
    and target_akreditasi_id. Returns 404 if the link does not exist.
    """
    unlink_evidence_indikator(
        db=db,
        evidence_id=evidence_id,
        indikator_id=indikator_id,
        target_akreditasi_id=target_akreditasi_id,
    )
