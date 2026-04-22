import uuid
from io import BytesIO

import openpyxl
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.lkps import LkpsSubmission, LkpsVmts
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/lkps/import", tags=["lkps-import"])


@router.post(
    "/{submission_id}",
    status_code=status.HTTP_200_OK,
    summary="Import LKPS data from Excel",
)
async def import_lkps_excel(
    submission_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengimpor data input LKPS dari file Excel (T-49).
    Membaca file .xlsx yang diunggah dan memasukkan datanya ke dalam database
    berdasarkan submission_id yang dipilih.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format file tidak valid. Harap unggah file Excel (.xlsx).",
        )

    # Validate submission exists
    submission = (
        db.query(LkpsSubmission).filter(LkpsSubmission.id == submission_id).first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LKPS Submission tidak ditemukan.",
        )

    # Read and load the workbook
    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(filename=BytesIO(contents), data_only=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal membaca file Excel: {str(e)}",
        )

    # ==========================================
    # Example parsing logic for Sheet "1" (VMTS)
    # ==========================================
    if "1" in wb.sheetnames:
        sheet = wb["1"]

        # Hapus data lama untuk sheet ini agar tidak duplikat
        db.query(LkpsVmts).filter(LkpsVmts.submission_id == submission_id).delete()

        # Iterasi baris. Mulai dari baris ke-7 (asumsi baris 1-6 adalah header/format baku LAM INFOKOM)
        for row in sheet.iter_rows(min_row=7, values_only=True):
            # Jika kolom "No" kosong, anggap baris tersebut kosong/selesai
            if row[0] is None:
                continue

            try:
                vmts = LkpsVmts(
                    submission_id=submission_id,
                    no=int(row[0]) if row[0] else None,
                    jenis_vmts=str(row[1]) if row[1] else None,
                    pernyataan=str(row[2]) if row[2] else None,
                    no_sk=str(row[3]) if row[3] else None,
                    link_dokumen=str(row[4]) if row[4] else None,
                )
                db.add(vmts)
            except Exception as e:
                # Log atau handle malformed data
                print(f"Error parsing row {row}: {e}")
                pass

    # TODO: Tambahkan logika parsing untuk sheet lainnya seperti Kerjasama (2a1), Mahasiswa, dll.
    # menggunakan model-model LKPS (LkpsKerjasama, LkpsMahasiswaAktif) sesuai format.

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan data ke database: {str(e)}",
        )

    return {
        "message": "Data LKPS berhasil diimpor dari Excel.",
        "submission_id": submission_id,
    }
