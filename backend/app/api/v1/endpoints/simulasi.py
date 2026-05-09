from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.simulasi import SimulasiRequest, SimulasiResponse
from app.services.simulasi import SimulasiService
from app.utils.dependencies import get_db

router = APIRouter()


@router.post("/hitung", response_model=SimulasiResponse)
def hitung_simulasi(request: SimulasiRequest, db: Session = Depends(get_db)):
    try:
        service = SimulasiService(db)
        return service.process_simulasi(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan server")
