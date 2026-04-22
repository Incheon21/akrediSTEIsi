from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.led import LEDResponse, LEDSaveRequest, LEDSaveResponse
from app.services.led import get_led_narasi, upsert_led_narasi
from app.services.led_exporter import generate_led_document
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/led", tags=["led"])


@router.post(
    "/narasi",
    response_model=LEDSaveResponse,
    summary="Create or update narasi LED",
    dependencies=[
        Depends(require_role("tim_prodi", "admin", "koordinator", "pimpinan"))
    ],
)
def save_narasi_led(
    body: LEDSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LEDSaveResponse:
    """
    Upsert narasi LED berdasarkan kombinasi target_akreditasi_id dan indikator_id.
    Validasi bisnis:
    - narasi tidak boleh kosong
    - tim_prodi hanya boleh mengakses target milik prodi sendiri
    """
    result = upsert_led_narasi(
        db=db,
        target_akreditasi_id=body.target_akreditasi_id,
        indikator_id=body.indikator_id,
        narasi=body.narasi,
        current_user=current_user,
    )

    return LEDSaveResponse(
        message="Narasi LED berhasil disimpan.",
        data=LEDResponse.model_validate(result),
    )


@router.get(
    "/narasi",
    response_model=LEDResponse,
    summary="Get narasi LED by target and indikator",
    dependencies=[
        Depends(require_role("tim_prodi", "admin", "koordinator", "pimpinan"))
    ],
)
def get_narasi_led(
    target_akreditasi_id: UUID,
    indikator_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LEDResponse:
    """
    Mengambil narasi LED berdasarkan target_akreditasi_id dan indikator_id.
    """
    result = get_led_narasi(
        db=db,
        target_akreditasi_id=target_akreditasi_id,
        indikator_id=indikator_id,
        current_user=current_user,
    )
    return LEDResponse.model_validate(result)


@router.get(
    "/export/{target_akreditasi_id}",
    summary="Export LED as Word Document",
    dependencies=[
        Depends(require_role("tim_prodi", "admin", "koordinator", "pimpinan"))
    ],
)
def export_led_word(
    target_akreditasi_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate dan unduh narasi laporan LED (Word) sesuai format baku LAM INFOKOM (T-42).
    """
    file_stream = generate_led_document(db, target_akreditasi_id)

    filename = f"Laporan_LED_{target_akreditasi_id}.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
