from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardMultiProdiResponse, ToggleTargetRequest
from app.services.dashboard import get_dashboard_multiprodi_data, toggle_target_akreditasi
from app.utils.dependencies import require_role

router = APIRouter(prefix="/multiprodi", tags=["dashboard-multiprodi"])

@router.get(
    "/dashboard",
    response_model=DashboardMultiProdiResponse,
    summary="Get aggregated dashboard data for all program studi"
)
def get_dashboard_prodi(
    tahun: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "pimpinan", "koordinator"))
) -> dict:
    return get_dashboard_multiprodi_data(db, tahun=tahun)

@router.post(
    "/toggle-target",
    summary="Toggle Target Akreditasi for a program studi in a specific year"
)
def toggle_target(
    req: ToggleTargetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "pimpinan", "koordinator"))
) -> dict:
    return toggle_target_akreditasi(db, req.program_studi_id, req.tahun, req.is_aktif)
