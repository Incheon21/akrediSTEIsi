from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import lkps
from app.api.v1.endpoints import program_studi

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(lkps.router)
api_router.include_router(program_studi.router)
