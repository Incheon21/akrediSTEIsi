import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.simulasi import IndikatorSimulasi, KomponenPenilaian, MatriksAkreditasi
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
