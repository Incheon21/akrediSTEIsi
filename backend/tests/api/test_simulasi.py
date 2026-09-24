import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lkps import LkpsSubmission
from app.models.program_studi import ProgramStudi
from app.models.simulasi import (
    IndikatorSimulasi,
    KomponenPenilaian,
    MatriksAkreditasi,
    SkorManualSimulasi,
)
from app.models.target_akreditasi import TargetAkreditasi
from app.services.simulasi import SimulasiService


def test_hitung_simulasi_endpoint(client: TestClient, db: Session):
    # Prepare dummy data for test
    matriks = MatriksAkreditasi(lembaga="TEKNIK", jenjang="SARJANA")
    db.add(matriks)
    db.flush()

    komponen_input = KomponenPenilaian(matriks_id=matriks.id, nama="Input", bobot=25.0)
    db.add(komponen_input)
    db.flush()

    indikator_1 = IndikatorSimulasi(
        komponen_id=komponen_input.id,
        kode_indikator="1",
        nama_indikator="Test Indikator",
        tipe_evaluasi="DIRECT_SCORE",
        konfigurasi_rumus={"min": 0, "max": 4},
    )
    db.add(indikator_1)
    db.commit()

    # Request payload
    payload = {
        "lembaga": "TEKNIK",
        "jenjang": "SARJANA",
        "data_input": [{"kode_indikator": "1", "nilai_input": 3.5}],
        "data_proses": [],
        "data_output": [],
    }

    # Call endpoint
    response = client.post("/api/v1/simulasi/hitung", json=payload)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "nilai_akhir" in data
    assert "status_prediksi" in data
    assert "breakdown_skor" in data
    assert data["breakdown_skor"]["Input"] == 87.5  # (3.5 / 1) * 25.0


def test_hitung_simulasi_not_found(client: TestClient):
    payload = {
        "lembaga": "UNKNOWN",
        "jenjang": "UNKNOWN",
        "data_input": [],
        "data_proses": [],
        "data_output": [],
    }

    response = client.post("/api/v1/simulasi/hitung", json=payload)
    assert response.status_code == 400
    assert "Matriks tidak ditemukan" in response.json()["detail"]


def test_formula_pdf_format_ribuan_dinormalisasi(db: Session):
    service = SimulasiService(db)

    assert service._evaluasi_formula("BOP / 5.000.000", {"BOP": 10000000}) == 2.0
    assert service._evaluasi_formula(
        "(2 * DPD) / 5.000.000", {"DPD": 5000000}
    ) == 2.0
    assert service._evaluasi_formula(
        "(4 * DPkMD) / 5.000.000", {"DPkMD": 2500000}
    ) == 2.0


def test_linear_scale_tetap_mengevaluasi_formula_di_nilai_minimum(db: Session):
    service = SimulasiService(db)
    indikator = IndikatorSimulasi(
        tipe_evaluasi="LINEAR_SCALE",
        konfigurasi_rumus={
            "min": 0,
            "max": 0.5,
            "formula": "1 + (6 * PPDMhs)",
        },
    )

    assert service._hitung_skor_mentah(indikator, 0) == 1.0


def test_simulasi_otomatis_mengelompokkan_indikator_penilaian(
    client: TestClient, db: Session
):
    prodi = ProgramStudi(kode="IF-SIM", nama="Informatika", jenjang="S1")
    db.add(prodi)
    db.flush()

    db.add(
        TargetAkreditasi(
            program_studi_id=prodi.id,
            tahun_akreditasi=2025,
            target_skor=300,
            is_aktif=True,
        )
    )
    submission = LkpsSubmission(program_studi_id=prodi.id, tahun_ts=2025)
    db.add(submission)

    matriks = MatriksAkreditasi(lembaga="TEKNIK", jenjang="SARJANA")
    db.add(matriks)
    db.flush()

    komponen = KomponenPenilaian(matriks_id=matriks.id, nama="Input", bobot=25.0)
    db.add(komponen)
    db.flush()

    for kode in ["1", "2", "9"]:
        db.add(
            IndikatorSimulasi(
                komponen_id=komponen.id,
                kode_indikator=kode,
                nama_indikator=f"Indikator {kode}",
                tipe_evaluasi="DIRECT_SCORE",
                konfigurasi_rumus={"min": 0, "max": 4},
            )
        )

    db.add(
        SkorManualSimulasi(
            submission_id=submission.id,
            kode_indikator="1",
            skor=3.0,
        )
    )
    db.commit()

    response = client.get(f"/api/v1/simulasi/otomatis/{prodi.id}")

    assert response.status_code == 200
    data = response.json()

    indikator_1 = next(
        item for item in data["semua_indikator"] if item["kode_indikator"] == "1"
    )
    indikator_9 = next(
        item for item in data["semua_indikator"] if item["kode_indikator"] == "9"
    )
    group_1 = next(item for item in data["kelompok_penilaian"] if item["id"] == "G1")
    group_2 = next(item for item in data["kelompok_penilaian"] if item["id"] == "G2")

    assert len(data["kelompok_penilaian"]) == 7
    assert indikator_1["kelompok_nama"] == "Diferensiasi Misi"
    assert indikator_1["subbab_kode"] == "1.1"
    assert indikator_9["kelompok_nama"] == "Akuntabilitas"
    assert indikator_9["subbab_kode"] == "2.3"
    assert group_1["jumlah_manual"] == 2
    assert group_1["jumlah_manual_terisi"] == 1
    assert group_1["sub_bab"][0]["jumlah_manual_terisi"] == 1
    assert group_2["jumlah_otomatis"] == 1


@pytest.mark.parametrize(
    "value, expected", [(0.1, 2.0), (0.2, 4.0), (0.5, 4.0), (0.75, 2.0)]
)
def test_piecewise_uses_restricted_conditions(db: Session, value, expected):
    service = SimulasiService(db)
    indikator = IndikatorSimulasi(
        tipe_evaluasi="PIECEWISE",
        konfigurasi_rumus={"conditions": [
            {"condition": "().__class__", "formula": "0"},
            {"condition": "PJP < 0.2", "formula": "20 * PJP"},
            {"condition": "0.2 <= PJP <= 0.5", "formula": "4"},
            {"condition": "PJP > 0.5", "formula": "8 - (8 * PJP)"},
        ]},
    )
    assert service._hitung_skor_mentah(indikator, value) == expected


def test_invalid_formula_preserves_zero_fallback(db: Session):
    service = SimulasiService(db)
    assert service._evaluasi_formula("().__class__", {}) == 0.0
    assert service._evaluasi_formula("1 / 0", {}) == 0.0
