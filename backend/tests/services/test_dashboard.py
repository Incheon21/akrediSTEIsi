from datetime import date, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.services.dashboard import (
    get_dashboard_multiprodi_data,
    get_dashboard_prodi_data,
)


def test_prodi_not_found(mock_db=MagicMock()):
    mock_db.query().filter().first.return_value = None

    with pytest.raises(Exception) as exc:
        get_dashboard_prodi_data(mock_db, uuid4())

    assert "Program Studi tidak ditemukan" in str(exc.value)


def test_no_active_target(mock_db=MagicMock()):
    prodi = MagicMock()
    prodi.id = uuid4()
    prodi.nama = "Informatika"
    prodi.jenjang = "S1"
    prodi.akreditasi = "A"
    prodi.tanggal_akreditasi = date(2022, 1, 1)

    mock_db.query().filter().first.return_value = prodi
    mock_db.query().filter().all.return_value = []  # no target

    result = get_dashboard_prodi_data(mock_db, prodi.id)

    assert result["program_studi_profile"]["is_active_accreditation"] is False
    assert result["lkps_percent"] == 0
    assert result["led_percent"] == 0


def test_active_target_with_deadline(mock_db=MagicMock()):
    prodi = MagicMock()
    prodi.id = uuid4()
    prodi.nama = "Informatika"
    prodi.jenjang = "S1"
    prodi.akreditasi = "A"
    prodi.tanggal_akreditasi = date(2022, 1, 1)

    target = MagicMock()
    target.id = uuid4()
    target.tahun_akreditasi = 2025
    target.is_aktif = True
    target.target_skor = 4.0
    target.deadline = date.today() + timedelta(days=10)

    # mock chaining
    mock_db.query().filter().first.return_value = prodi
    mock_db.query().filter().all.return_value = [target]

    # mock kriteria kosong biar simpel
    mock_db.query().order_by().all.return_value = []

    result = get_dashboard_prodi_data(mock_db, prodi.id)

    assert result["program_studi_profile"]["is_active_accreditation"] is True
    assert result["current_year"] == 2025
    assert result["days_remaining"] <= 10
    assert len(result["early_warnings"]) >= 1


def test_recommendation_generated():
    mock_db = MagicMock()

    prodi = MagicMock()
    prodi.id = uuid4()
    prodi.nama = "Informatika"
    prodi.jenjang = "S1"
    prodi.akreditasi = None
    prodi.tanggal_akreditasi = None

    target = MagicMock()
    target.id = uuid4()
    target.tahun_akreditasi = 2025
    target.is_aktif = True
    target.deadline = date.today() + timedelta(days=10)
    target.target_skor = 3.5

    kriteria = MagicMock()
    kriteria.kode = "K1"
    kriteria.nama = "Kriteria 1"
    kriteria.id = uuid4()

    indikator = MagicMock()
    indikator.id = uuid4()
    indikator.tipe_input = "manual"

    # 🔥 IMPORTANT: differentiate query per model
    def query_side_effect(model):
        q = MagicMock()

        if model.__name__ == "ProgramStudi":
            q.filter().first.return_value = prodi

        elif model.__name__ == "TargetAkreditasi":
            q.filter().all.return_value = [target]

        elif model.__name__ == "Kriteria":
            q.order_by().all.return_value = [kriteria]

        elif model.__name__ == "Indikator":
            q.filter().all.return_value = [indikator]

        elif model.__name__ in ["DataLKPS", "NarasiLED", "EvidenceIndikator"]:
            q.filter().count.return_value = 0

        return q

    mock_db.query.side_effect = query_side_effect

    result = get_dashboard_prodi_data(mock_db, prodi.id)

    assert len(result["recommendation_messages"]) > 0


def test_multi_prodi(mock_db=MagicMock()):
    prodi1 = MagicMock()
    prodi1.id = uuid4()

    prodi2 = MagicMock()
    prodi2.id = uuid4()

    mock_db.query().all.return_value = [prodi1, prodi2]

    # mock inner function
    mock_result = {
        "program_studi_profile": {
            "name": "Test",
            "degree": "S1",
            "last_accreditation_status": "A",
            "last_accreditation_year": 2020,
            "is_active_accreditation": True,
        },
        "lkps_percent": 10,
        "led_percent": 20,
        "evidence_percent": 30,
        "score_value": 0.0,
        "target_score": 3.5,
        "days_remaining": 10,
    }

    from app.services import dashboard

    dashboard.get_dashboard_prodi_data = MagicMock(return_value=mock_result)

    result = get_dashboard_multiprodi_data(mock_db)

    assert len(result["prodi_list"]) == 2
