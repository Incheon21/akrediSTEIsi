from uuid import uuid4

from fastapi.testclient import TestClient


def test_get_dashboard_prodi(
    client, monkeypatch, mock_dashboard_prodi_response, admin_token
):
    prodi_id = uuid4()

    monkeypatch.setattr(
        "app.api.v1.endpoints.dashboard.get_dashboard_prodi_data",
        lambda db, prodi_id, tahun=None: mock_dashboard_prodi_response,
    )

    response = client.get(
        f"/api/v1/prodi/{prodi_id}/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["program_studi_profile"]["name"] == "Informatika"


def test_get_dashboard_multiprodi(
    client, monkeypatch, mock_dashboard_multi_response, admin_token
):
    monkeypatch.setattr(
        "app.api.v1.endpoints.dashboard_multiprodi.get_dashboard_multiprodi_data",
        lambda db, tahun=None: mock_dashboard_multi_response,
    )

    response = client.get(
        "/api/v1/multiprodi/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["prodi_list"]) == 1
