import io
import uuid

import openpyxl
import pytest

from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.lkps import LkpsPenelitianMahasiswa, LkpsPrasarana, LkpsSubmission, LkpsVmts
from app.models.narasi_led import NarasiLED
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_xlsx(sheet_data: dict[str, list[list]]) -> bytes:
    """
    Build a minimal .xlsx file in memory.
    sheet_data: { "sheetname": [[row1col1, row1col2, ...], [row2col1, ...], ...] }
    Rows are written starting from row 1.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet

    for sheet_name, rows in sheet_data.items():
        ws = wb.create_sheet(title=sheet_name)
        for row in rows:
            ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def seeded_progress_context(db, admin_user):
    """
    Seeds a minimal chain:
      ProgramStudi → TargetAkreditasi
      Kriteria → Indikator (tipe_input="narasi")  ← LED-type
      Kriteria → Indikator (tipe_input="tabel")   ← LKPS-type
      LkpsSubmission for same prodi + year
    Returns a dict with all created objects.
    """
    prodi = ProgramStudi(
        kode=f"PR-{uuid.uuid4().hex[:6]}",
        nama="Prodi Progress Test",
        jenjang="S1",
        status="aktif",
    )
    db.add(prodi)
    db.flush()

    target = TargetAkreditasi(
        program_studi_id=prodi.id,
        tahun_akreditasi=2030,
        target_skor=3.5,
        is_aktif=True,
        notifikasi_aktif=True,
    )
    db.add(target)
    db.flush()

    lkps_sub = LkpsSubmission(
        program_studi_id=prodi.id,
        tahun_ts=2030,
        status="draft",
    )
    db.add(lkps_sub)
    db.flush()

    kriteria = Kriteria(
        kode=f"C-{uuid.uuid4().hex[:4]}",
        nama="Kriteria Progress Test",
    )
    db.add(kriteria)
    db.flush()

    ind_narasi = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-NAR-{uuid.uuid4().hex[:4]}",
        deskripsi="Indikator narasi / LED",
        tipe_input="narasi",
    )
    ind_tabel = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-TAB-{uuid.uuid4().hex[:4]}",
        deskripsi="Indikator tabel / LKPS",
        tipe_input="tabel",
    )
    db.add(ind_narasi)
    db.add(ind_tabel)
    db.commit()
    db.refresh(target)
    db.refresh(ind_narasi)
    db.refresh(ind_tabel)

    return {
        "prodi": prodi,
        "target": target,
        "lkps_sub": lkps_sub,
        "kriteria": kriteria,
        "ind_narasi": ind_narasi,
        "ind_tabel": ind_tabel,
    }


@pytest.fixture()
def seeded_submission(db, admin_user):
    """Seeds a minimal ProgramStudi + LkpsSubmission for import tests."""
    prodi = ProgramStudi(
        kode=f"IMP-{uuid.uuid4().hex[:6]}",
        nama="Prodi Import Test",
        jenjang="S1",
        status="aktif",
    )
    db.add(prodi)
    db.flush()

    submission = LkpsSubmission(
        program_studi_id=prodi.id,
        tahun_ts=2030,
        status="draft",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {"prodi": prodi, "submission": submission}


# ─────────────────────────────────────────────────────────────────────────────
# T-46: GET /indikator/progress/status
# ─────────────────────────────────────────────────────────────────────────────


def test_progress_status_returns_correct_structure(
    client, db, seeded_progress_context, admin_token
):
    """The endpoint should return the expected top-level keys and indicator list."""
    target = seeded_progress_context["target"]

    response = client.get(
        f"/api/v1/indikator/progress/status?target_akreditasi_id={target.id}",
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()

    assert "target_akreditasi_id" in body
    assert "total_indicators" in body
    assert "completed_indicators" in body
    assert "overall_progress_percentage" in body
    assert "indicators" in body
    assert isinstance(body["indicators"], list)

    for ind in body["indicators"]:
        assert "indikator_id" in ind
        assert "kode_indikator" in ind
        assert "tipe_input" in ind
        assert "completion_percentage" in ind
        assert "is_complete" in ind


def test_progress_status_narasi_complete_when_filled(
    client, db, seeded_progress_context, admin_token
):
    """A narasi-type indicator should be complete once a NarasiLED row is saved."""
    ctx = seeded_progress_context
    target = ctx["target"]
    ind_narasi = ctx["ind_narasi"]

    # Save a narasi for the LED indicator
    narasi = NarasiLED(
        target_akreditasi_id=target.id,
        indikator_id=ind_narasi.id,
        narasi="Narasi sudah diisi untuk pengujian.",
    )
    db.add(narasi)
    db.commit()

    response = client.get(
        f"/api/v1/indikator/progress/status?target_akreditasi_id={target.id}",
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()

    # Find the narasi indicator in the response
    narasi_entry = next(
        (i for i in body["indicators"] if i["indikator_id"] == str(ind_narasi.id)),
        None,
    )
    assert narasi_entry is not None
    assert narasi_entry["is_complete"] is True
    assert narasi_entry["completion_percentage"] == 100.0


def test_progress_status_narasi_incomplete_when_empty(
    client, db, seeded_progress_context, admin_token
):
    """A narasi-type indicator without a NarasiLED row should be incomplete."""
    ctx = seeded_progress_context
    target = ctx["target"]
    ind_narasi = ctx["ind_narasi"]

    response = client.get(
        f"/api/v1/indikator/progress/status?target_akreditasi_id={target.id}",
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()

    narasi_entry = next(
        (i for i in body["indicators"] if i["indikator_id"] == str(ind_narasi.id)),
        None,
    )
    assert narasi_entry is not None
    assert narasi_entry["is_complete"] is False
    assert narasi_entry["completion_percentage"] == 0.0


def test_progress_status_target_not_found(client, admin_token):
    """Should return 404 for a nonexistent target_akreditasi_id."""
    response = client.get(
        f"/api/v1/indikator/progress/status?target_akreditasi_id={uuid.uuid4()}",
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == 404


def test_progress_status_unauthorized(client, db, seeded_progress_context):
    """Should return 401 when no auth token is provided."""
    target = seeded_progress_context["target"]

    response = client.get(
        f"/api/v1/indikator/progress/status?target_akreditasi_id={target.id}",
    )
    assert response.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# T-49: POST /lkps/import/{submission_id}
# ─────────────────────────────────────────────────────────────────────────────


def test_import_lkps_excel_success(client, seeded_submission, admin_token):
    """A valid .xlsx with Sheet '1' data rows should be imported successfully."""
    submission = seeded_submission["submission"]

    # Build a minimal xlsx matching the LAM INFOKOM Sheet "1" (VMTS) format.
    # Rows 1-6 are headers; actual data starts at row 7.
    rows = [
        ["Tabel 1 Visi Misi...", None, None, None, None],  # row 1 (header)
        [None, None, None, None, None],  # row 2
        ["Diisi oleh pengusul...", None, None, None, None],  # row 3
        ["No.", "Jenis VMTS", "Pernyataan", "No. SK", "Link Dokumen"],  # row 4
        [None, None, None, None, None],  # row 5
        [1, 2, 3, 4, 5],  # row 6 (col ref numbers)
        [
            1,
            "VMTS PT",
            "Visi ITB adalah ...",
            "SK-001",
            "http://link.com",
        ],  # row 7 ← data
        [2, None, "Misi ITB adalah ...", None, None],  # row 8 ← data
    ]
    xlsx_bytes = _make_xlsx({"1": rows})

    response = client.post(
        f"/api/v1/lkps/import/{submission.id}",
        files={
            "file": (
                "lkps.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()
    assert "berhasil" in body["message"].lower()
    assert body["submission_id"] == str(submission.id)


def test_import_lkps_invalid_file_type(client, seeded_submission, admin_token):
    """Uploading a non-.xlsx file should return 400."""
    submission = seeded_submission["submission"]

    response = client.post(
        f"/api/v1/lkps/import/{submission.id}",
        files={"file": ("data.csv", b"col1,col2\nval1,val2", "text/csv")},
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 400
    assert (
        "tidak valid" in response.json()["detail"].lower()
        or "xlsx" in response.json()["detail"].lower()
    )


def test_import_lkps_submission_not_found(client, admin_token):
    """Importing to a nonexistent submission_id should return 404."""
    xlsx_bytes = _make_xlsx(
        {"1": [[1, "VMTS PT", "Visi", "SK-001", "http://link.com"]]}
    )

    response = client.post(
        f"/api/v1/lkps/import/{uuid.uuid4()}",
        files={
            "file": (
                "lkps.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 404


def test_import_lkps_handles_blank_rows(client, seeded_submission, admin_token):
    """Blank rows in the Excel file should be skipped gracefully without error."""
    submission = seeded_submission["submission"]

    # Mix of data rows and fully blank rows
    rows = [
        [None, None, None, None, None],  # rows 1-6: headers (all blank for simplicity)
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [1, "VMTS PT", "Pernyataan valid", "SK-001", "http://link.com"],  # row 7: valid
        [None, None, None, None, None],  # row 8: blank — should be skipped
        [2, None, "Pernyataan lain", None, None],  # row 9: valid but sparse
    ]
    xlsx_bytes = _make_xlsx({"1": rows})

    response = client.post(
        f"/api/v1/lkps/import/{submission.id}",
        files={
            "file": (
                "lkps.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200


def test_import_lkps_carries_forward_grouped_fields(client, db, seeded_submission, admin_token):
    """Continuation rows should inherit the previous non-empty category/group cells."""
    submission = seeded_submission["submission"]

    rows_vmts = [
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [1, "VMTS PT", "Visi PT", "SK-PT", "https://pt.example"],
        [2, None, "Misi PT lanjutan", "SK-PT-2", "https://pt2.example"],
        [3, "Visi Keilmuan PS", "Visi PS", "SK-PS", "https://ps.example"],
        [4, None, "Misi PS lanjutan", "SK-PS-2", "https://ps2.example"],
    ]
    rows_5a = [[None] * 12 for _ in range(9)] + [
        [1, "Laboratorium Komputasi", 1, "Server", 2, 2, "V", None, "V", None, "V", None],
        [2, None, None, "Workstation", 20, 18, "V", None, "V", None, "V", None],
    ]
    rows_6h1 = [[None] * 6 for _ in range(10)] + [
        [1, "Dosen A", "AI", "Mahasiswa 1", "Penelitian 1", 2030],
        [2, None, None, "Mahasiswa 2", "Penelitian 2", 2030],
    ]
    xlsx_bytes = _make_xlsx({"1": rows_vmts, "5a": rows_5a, "6h1": rows_6h1})

    response = client.post(
        f"/api/v1/lkps/import/{submission.id}",
        files={
            "file": (
                "lkps.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200

    vmts_rows = (
        db.query(LkpsVmts)
        .filter(LkpsVmts.submission_id == submission.id)
        .order_by(LkpsVmts.no)
        .all()
    )
    assert [row.jenis_vmts for row in vmts_rows] == [
        "VMTS PT",
        "VMTS PT",
        "Visi Keilmuan PS",
        "Visi Keilmuan PS",
    ]

    prasarana_rows = (
        db.query(LkpsPrasarana)
        .filter(LkpsPrasarana.submission_id == submission.id)
        .order_by(LkpsPrasarana.no)
        .all()
    )
    assert [row.nama_prasarana for row in prasarana_rows] == [
        "Laboratorium Komputasi",
        "Laboratorium Komputasi",
    ]
    assert [row.jumlah_prasarana for row in prasarana_rows] == [1, 1]

    penelitian_rows = (
        db.query(LkpsPenelitianMahasiswa)
        .filter(LkpsPenelitianMahasiswa.submission_id == submission.id)
        .order_by(LkpsPenelitianMahasiswa.no)
        .all()
    )
    assert [row.nama_dosen for row in penelitian_rows] == ["Dosen A", "Dosen A"]
    assert [row.tema_penelitian for row in penelitian_rows] == ["AI", "AI"]


def test_import_lkps_unauthorized(client, seeded_submission):
    """Importing without a token should return 401."""
    submission = seeded_submission["submission"]
    xlsx_bytes = _make_xlsx({"1": []})

    response = client.post(
        f"/api/v1/lkps/import/{submission.id}",
        files={
            "file": (
                "lkps.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 401
