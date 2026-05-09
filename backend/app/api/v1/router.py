from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    dashboard,
    dashboard_multiprodi,
    evidence,
    indikator,
    led,
    lkps,
    lkps_import,
    program_studi,
    target_akreditasi,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(lkps.router)
api_router.include_router(lkps_import.router)
api_router.include_router(program_studi.router)
api_router.include_router(dashboard.router)
api_router.include_router(dashboard_multiprodi.router)
api_router.include_router(indikator.router)
api_router.include_router(led.router)
api_router.include_router(evidence.router)
api_router.include_router(target_akreditasi.router)
