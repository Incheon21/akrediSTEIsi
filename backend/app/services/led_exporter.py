import io
from pathlib import Path
from uuid import UUID

from docxtpl import DocxTemplate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.indikator import Indikator
from app.models.narasi_led import NarasiLED
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi

# Lokasi template file .docx di root backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_PATH = BASE_DIR / "template-ledps.docx"


def generate_led_document(db: Session, target_akreditasi_id: UUID) -> io.BytesIO:
    """
    Generate dokumen Word (.docx) untuk Laporan Evaluasi Diri (LED)
    berdasarkan data narasi yang ada di database.
    """
    # 1. Ambil data Target Akreditasi & Program Studi
    target = (
        db.query(TargetAkreditasi)
        .filter(TargetAkreditasi.id == target_akreditasi_id)
        .first()
    )
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target Akreditasi tidak ditemukan.",
        )

    prodi = (
        db.query(ProgramStudi)
        .filter(ProgramStudi.id == target.program_studi_id)
        .first()
    )
    prodi_name = prodi.nama if prodi else "Program Studi"
    jenjang = prodi.jenjang if prodi else "S1"

    # 2. Ambil seluruh data Narasi LED untuk target ini beserta info Indikatornya
    narasies = (
        db.query(NarasiLED, Indikator)
        .join(Indikator, NarasiLED.indikator_id == Indikator.id)
        .filter(NarasiLED.target_akreditasi_id == target_akreditasi_id)
        .all()
    )

    # 3. Bangun dictionary context untuk di-render oleh docxtpl
    # Dictionary `narasi` akan menyimpan teks berdasarkan kode indikator.
    # Contoh di template docx: {{ narasi['A_1'] }} atau {{ narasi_A_1 }}
    narasi_dict = {}

    for narasi_obj, indikator_obj in narasies:
        kode = indikator_obj.kode_indikator
        # Buat key yang aman untuk variabel template (ubah titik/strip jadi underscore)
        safe_code = kode.replace(".", "_").replace("-", "_")

        teks_narasi = narasi_obj.narasi or ""

        narasi_dict[kode] = teks_narasi
        narasi_dict[safe_code] = teks_narasi

    # Data utama yang akan disisipkan ke template
    context = {
        "prodi_name": prodi_name,
        "jenjang": jenjang,
        "tahun": target.tahun_akreditasi,
        "narasi": narasi_dict,
    }

    # Expose top-level narasi_* keys so {{ narasi_C_1_1 }} style tags work directly
    # e.g. kode "C.1.1" → context key "narasi_C_1_1"
    for safe_code, teks in narasi_dict.items():
        # Only add the safe (dot/dash-free) versions as top-level keys
        if "." not in safe_code and "-" not in safe_code:
            context[f"narasi_{safe_code}"] = teks

    # 4. Validasi file template
    if not TEMPLATE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File template LED (template-ledps.docx) tidak ditemukan di server.",
        )

    # 5. Render dokumen menggunakan docxtpl
    try:
        doc = DocxTemplate(str(TEMPLATE_PATH))
        doc.render(context)

        # Simpan ke dalam memory stream (BytesIO) agar tidak perlu file sementara di disk
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        return file_stream
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal men-generate dokumen LED: {str(e)}",
        )
