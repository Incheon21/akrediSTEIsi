from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardProdiResponse
from app.services.dashboard import get_dashboard_prodi_data
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/prodi", tags=["dashboard-prodi"])

@router.get(
    "/{prodi_id}/dashboard",
    response_model=DashboardProdiResponse,
    summary="Get aggregated dashboard data for a program studi"
)
def get_dashboard_prodi(
    prodi_id: UUID,
    tahun: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    return get_dashboard_prodi_data(db, prodi_id, tahun)
