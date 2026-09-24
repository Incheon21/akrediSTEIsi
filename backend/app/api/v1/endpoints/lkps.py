"""LKPS API endpoints.

Provides:
  - Submission CRUD
  - Section progress tracking
  - Excel export (GET /submissions/{id}/export)
  - Template management (upload / list)
"""

from __future__ import annotations

import os
import shutil
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Date as SADate, DateTime as SADateTime, Integer as SAInteger, Numeric, String as SAString

from app.api.v1.endpoints.lkps_sections import SectionBinding, get_section_binding
from app.db import get_db
from app.models.lkps import (
    LkpsSubmission,
    LkpsSectionProgress,
    LkpsTemplate,
)
from app.models.program_studi import ProgramStudi
from app.services.excel_export.lkps_exporter import LkpsExporter
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/lkps", tags=["lkps"])

# Directory where uploaded templates are stored
TEMPLATE_DIR = Path(os.getenv("TEMPLATE_STORAGE_DIR", "storage/templates"))
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Template management
# ---------------------------------------------------------------------------

@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    rows = db.execute(select(LkpsTemplate).order_by(LkpsTemplate.uploaded_at.desc())).scalars().all()
    return [
        {
            "id": str(t.id),
            "version": t.version,
            "filename": t.filename,
            "is_active": t.is_active,
            "uploaded_at": t.uploaded_at,
        }
        for t in rows
    ]


@router.post("/templates", status_code=status.HTTP_201_CREATED)
def upload_template(
    version: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are accepted.")

    dest = TEMPLATE_DIR / f"template-lkps-{version}.xlsx"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    template = LkpsTemplate(
        version=version,
        filename=file.filename,
        file_path=str(dest),
        is_active=True,
        uploaded_by=current_user.id,
    )
    # Deactivate previous active templates
    db.execute(
        LkpsTemplate.__table__.update()
        .where(LkpsTemplate.id != template.id)
        .values(is_active=False)
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"id": str(template.id), "version": template.version}


# ---------------------------------------------------------------------------
# Submission CRUD
# ---------------------------------------------------------------------------

@router.get("/submissions")
def list_submissions(
    program_studi_id: str | None = None,
    db: Session = Depends(get_db),
):
    q = select(LkpsSubmission)
    if program_studi_id:
        q = q.where(LkpsSubmission.program_studi_id == uuid.UUID(program_studi_id))
    rows = db.execute(q.order_by(LkpsSubmission.tahun_ts.desc())).scalars().all()
    return [_submission_dict(s) for s in rows]


@router.post("/submissions", status_code=status.HTTP_201_CREATED)
def create_submission(
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ps_id = uuid.UUID(body["program_studi_id"])
    tahun_ts = int(body["tahun_ts"])

    # Validate prodi exists
    ps = db.get(ProgramStudi, ps_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Program studi not found.")

    # Resolve active template
    template = db.execute(
        select(LkpsTemplate).where(LkpsTemplate.is_active.is_(True))
    ).scalar_one_or_none()

    sub = LkpsSubmission(
        program_studi_id=ps_id,
        template_id=template.id if template else None,
        tahun_ts=tahun_ts,
        status="draft",
        nama_pengusul=body.get("nama_pengusul"),
        submitted_by=current_user.id,
    )
    db.add(sub)
    db.flush()

    # Seed section progress rows for all 52 LKPS sections
    section_codes = [
        "PS", "PSPPI", "1",
        "2a1", "2a2", "2a3", "2b",
        "3a1", "3a2", "3a3", "3a4", "3a5", "3b", "3c",
        "4a", "4b", "4c", "4d", "4e",
        "4f-1", "4f-2", "4f-3", "4f-4",
        "4g", "4h", "4i", "4j", "4k",
        "5a", "5b", "5c",
        "6a", "6b", "6c1", "6c2", "6d",
        "6e1", "6e2", "6e3-1", "6e3-2", "6e3-3", "6e3-4", "6e4",
        "6f1", "6f2", "6g1", "6g2", "6h1", "6h2", "6i",
        "7a", "7b",
    ]
    for code in section_codes:
        db.add(LkpsSectionProgress(
            submission_id=sub.id,
            section_code=code,
            status="not_started",
            completion_pct=0,
            last_updated_by=current_user.id,
        ))

    db.commit()
    db.refresh(sub)
    return _submission_dict(sub)


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(LkpsSubmission, uuid.UUID(submission_id))
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return _submission_dict(sub)


@router.patch("/submissions/{submission_id}")
def update_submission(
    submission_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    sub = db.get(LkpsSubmission, uuid.UUID(submission_id))
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found.")
    for field in ("status", "nama_pengusul", "tanggal_pengajuan"):
        if field in body:
            setattr(sub, field, body[field])
    db.commit()
    db.refresh(sub)
    return _submission_dict(sub)


# ---------------------------------------------------------------------------
# Section progress
# ---------------------------------------------------------------------------

@router.get("/submissions/{submission_id}/progress")
def get_progress(submission_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(LkpsSectionProgress)
        .where(LkpsSectionProgress.submission_id == uuid.UUID(submission_id))
        .order_by(LkpsSectionProgress.section_code)
    ).scalars().all()
    return [
        {
            "section_code": r.section_code,
            "status": r.status,
            "completion_pct": r.completion_pct,
            "notes": r.notes,
            "last_updated_at": r.last_updated_at,
        }
        for r in rows
    ]


@router.patch("/submissions/{submission_id}/progress/{section_code}")
def update_progress(
    submission_id: str,
    section_code: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prog = db.execute(
        select(LkpsSectionProgress)
        .where(
            LkpsSectionProgress.submission_id == uuid.UUID(submission_id),
            LkpsSectionProgress.section_code == section_code,
        )
    ).scalar_one_or_none()
    if not prog:
        raise HTTPException(status_code=404, detail="Section progress not found.")
    for field in ("status", "completion_pct", "notes"):
        if field in body:
            setattr(prog, field, body[field])
    prog.last_updated_by = current_user.id
    db.commit()
    return {"section_code": prog.section_code, "status": prog.status, "completion_pct": prog.completion_pct}


# ---------------------------------------------------------------------------
# Section records (data entry)
# ---------------------------------------------------------------------------


@router.get("/submissions/{submission_id}/sections/{section_code}/records")
def list_section_records(
    submission_id: str,
    section_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ = current_user  # authenticated access only
    submission_uuid = _parse_uuid(submission_id, "submission_id")
    binding = _require_section_binding(section_code)
    _assert_submission_exists(db, submission_uuid)
    rows = _fetch_section_rows(db, submission_uuid, binding)
    return [_serialize_instance(row) for row in rows]


@router.post(
    "/submissions/{submission_id}/sections/{section_code}/records",
    status_code=status.HTTP_201_CREATED,
)
def create_section_record(
    submission_id: str,
    section_code: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ = current_user
    submission_uuid = _parse_uuid(submission_id, "submission_id")
    binding = _require_section_binding(section_code)
    _assert_submission_exists(db, submission_uuid)

    instance = binding.model(submission_id=submission_uuid)
    _apply_payload(instance, body, binding)
    db.add(instance)
    _safe_commit(db)
    db.refresh(instance)
    return _serialize_instance(instance)


@router.patch("/submissions/{submission_id}/sections/{section_code}/records/{record_id}")
def update_section_record(
    submission_id: str,
    section_code: str,
    record_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ = current_user
    submission_uuid = _parse_uuid(submission_id, "submission_id")
    record_uuid = _parse_uuid(record_id, "record_id")
    binding = _require_section_binding(section_code)
    record = _get_section_record(db, binding, submission_uuid, record_uuid)
    _apply_payload(record, body, binding)
    _safe_commit(db)
    db.refresh(record)
    return _serialize_instance(record)


@router.delete("/submissions/{submission_id}/sections/{section_code}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section_record(
    submission_id: str,
    section_code: str,
    record_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ = current_user
    submission_uuid = _parse_uuid(submission_id, "submission_id")
    record_uuid = _parse_uuid(record_id, "record_id")
    binding = _require_section_binding(section_code)
    record = _get_section_record(db, binding, submission_uuid, record_uuid)
    db.delete(record)
    _safe_commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Excel export — the core endpoint
# ---------------------------------------------------------------------------

@router.get("/submissions/{submission_id}/export")
def export_submission(
    submission_id: str,
    db: Session = Depends(get_db),
):
    """Generate and return a filled LKPS .xlsx file.

    The file is produced by injecting submission data into the original
    template so all formulas, protection, and formatting are preserved.
    """
    sub = db.get(LkpsSubmission, uuid.UUID(submission_id))
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Resolve template path
    if sub.template_id:
        template_obj = db.get(LkpsTemplate, sub.template_id)
        template_path = template_obj.file_path if template_obj else None
    else:
        template_path = None

    # Fallback to the bundled template shipped with the backend
    if not template_path or not Path(template_path).exists():
        template_path = str(Path(__file__).parents[4] / "template-lkps.xlsx")

    if not Path(template_path).exists():
        raise HTTPException(status_code=500, detail="LKPS template file not found on server.")

    exporter = LkpsExporter(template_path=template_path)
    file_bytes = exporter.generate(submission=sub, db=db)

    ps_nama = sub.program_studi.nama.replace(" ", "_") if sub.program_studi else "PS"
    filename = f"LKPS_{ps_nama}_{sub.tahun_ts}.xlsx"

    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _parse_uuid(value: str, field_name: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} supplied.") from exc


def _require_section_binding(section_code: str) -> SectionBinding:
    binding = get_section_binding(section_code)
    if not binding:
        raise HTTPException(status_code=404, detail=f"Section {section_code} is not editable via API.")
    return binding


def _assert_submission_exists(db: Session, submission_uuid: uuid.UUID) -> None:
    if not db.get(LkpsSubmission, submission_uuid):
        raise HTTPException(status_code=404, detail="Submission not found.")


def _fetch_section_rows(db: Session, submission_uuid: uuid.UUID, binding: SectionBinding):
    query = select(binding.model).where(binding.model.submission_id == submission_uuid)
    for column, expected in binding.enforced_values.items():
        query = query.where(getattr(binding.model, column) == expected)
    if binding.order_by:
        order_columns = [getattr(binding.model, col) for col in binding.order_by]
        query = query.order_by(*order_columns)
    return db.execute(query).scalars().all()


def _get_section_record(
    db: Session,
    binding: SectionBinding,
    submission_uuid: uuid.UUID,
    record_uuid: uuid.UUID,
):
    record = db.get(binding.model, record_uuid)
    if not record or record.submission_id != submission_uuid:
        raise HTTPException(status_code=404, detail="Record not found.")
    for key, expected in binding.enforced_values.items():
        if getattr(record, key) != expected:
            raise HTTPException(status_code=404, detail="Record not found.")
    return record


def _apply_payload(target, payload: dict, binding: SectionBinding) -> None:
    mapper = sa_inspect(binding.model)
    columns = {c.key: c for c in mapper.columns}
    immutable = {"id", "submission_id"}
    for key, value in binding.enforced_values.items():
        setattr(target, key, value)
    for key, raw in payload.items():
        if key in immutable or key in binding.enforced_values:
            continue
        column = columns.get(key)
        if column is None:
            continue
        setattr(target, key, _coerce_value(column, raw))


def _coerce_value(column, raw):
    if raw is None:
        return None
    # Empty string: keep as-is for String columns (they may be non-nullable),
    # but treat as None for numeric/date types
    if raw == "":
        if isinstance(column.type, SAString):
            return raw
        return None
    col_type = column.type
    if isinstance(col_type, (SAInteger, BigInteger)):
        return int(raw)
    if isinstance(col_type, Numeric):
        return Decimal(str(raw))
    if isinstance(col_type, Boolean):
        if isinstance(raw, str):
            return raw.lower() in {"true", "1", "yes", "y"}
        return bool(raw)
    if isinstance(col_type, SADate):
        if isinstance(raw, date):
            return raw
        return date.fromisoformat(str(raw))
    if isinstance(col_type, SADateTime):
        if isinstance(raw, datetime):
            return raw
        return datetime.fromisoformat(str(raw))
    return raw


def _serialize_instance(instance) -> dict:
    mapper = sa_inspect(instance.__class__)
    data: dict[str, Any] = {}
    for column in mapper.columns:
        value = getattr(instance, column.key)
        if isinstance(value, uuid.UUID):
            data[column.key] = str(value)
        elif isinstance(value, Decimal):
            data[column.key] = float(value)
        elif isinstance(value, datetime):
            data[column.key] = value.isoformat()
        elif isinstance(value, date):
            data[column.key] = value.isoformat()
        else:
            data[column.key] = value
    return data


def _safe_commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig)) from exc


def _submission_dict(sub: LkpsSubmission) -> dict:
    return {
        "id": str(sub.id),
        "program_studi_id": str(sub.program_studi_id),
        "template_id": str(sub.template_id) if sub.template_id else None,
        "tahun_ts": sub.tahun_ts,
        "status": sub.status,
        "nama_pengusul": sub.nama_pengusul,
        "tanggal_pengajuan": sub.tanggal_pengajuan,
        "submitted_at": sub.submitted_at,
        "created_at": sub.created_at,
    }
