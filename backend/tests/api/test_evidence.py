import uuid

import pytest
from fastapi import status

from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.program_studi import ProgramStudi
from app.models.target_akreditasi import TargetAkreditasi


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def dummy_pdf_file():
    """Returns a dummy PDF file for upload tests."""
    return ("dummy.pdf", b"%PDF-1.4 dummy content", "application/pdf")


@pytest.fixture
def seeded_indikator_and_target(db, admin_user):
    """Seeds a minimal ProgramStudi -> TargetAkreditasi -> Kriteria -> Indikator chain."""
    prodi = ProgramStudi(
        kode=f"TS-{uuid.uuid4().hex[:6]}",
        nama="Test Prodi Evidence",
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

    kriteria = Kriteria(
        kode=f"C-{uuid.uuid4().hex[:4]}",
        nama="Kriteria Test",
    )
    db.add(kriteria)
    db.flush()

    indikator = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-{uuid.uuid4().hex[:6]}",
        deskripsi="Indikator test untuk evidence linking",
        tipe_input="teks",
    )
    db.add(indikator)
    db.commit()
    db.refresh(target)
    db.refresh(indikator)

    return {"target": target, "indikator": indikator}


def test_upload_evidence_success(authorized_client, dummy_pdf_file):
    data = {
        "judul": "Test Evidence Document",
        "deskripsi": "This is a test description",
        "is_global": "true",
    }
    files = {"file": dummy_pdf_file}

    response = authorized_client.post("/api/v1/evidence/", data=data, files=files)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["judul"] == "Test Evidence Document"
    assert response_data["deskripsi"] == "This is a test description"
    assert response_data["is_global"] is True
    assert "id" in response_data
    assert "url_file" in response_data
    assert response_data["tipe_file"] == "application/pdf"


def test_upload_evidence_invalid_extension(authorized_client):
    data = {"judul": "Invalid File"}
    files = {"file": ("test.txt", b"plain text content", "text/plain")}

    response = authorized_client.post("/api/v1/evidence/", data=data, files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not allowed" in response.json()["detail"].lower()


def test_get_evidence_list(authorized_client, dummy_pdf_file):
    # Upload first
    authorized_client.post(
        "/api/v1/evidence/", data={"judul": "Doc 1"}, files={"file": dummy_pdf_file}
    )

    response = authorized_client.get("/api/v1/evidence/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_evidence_by_id(authorized_client, dummy_pdf_file):
    # Upload
    upload_res = authorized_client.post(
        "/api/v1/evidence/",
        data={"judul": "Specific Doc"},
        files={"file": dummy_pdf_file},
    )
    evidence_id = upload_res.json()["id"]

    # Get by ID
    response = authorized_client.get(f"/api/v1/evidence/{evidence_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == evidence_id
    assert response.json()["judul"] == "Specific Doc"


def test_download_evidence(authorized_client, dummy_pdf_file):
    # Upload
    upload_res = authorized_client.post(
        "/api/v1/evidence/",
        data={"judul": "Downloadable Doc"},
        files={"file": dummy_pdf_file},
    )
    evidence_id = upload_res.json()["id"]

    # Download
    response = authorized_client.get(f"/api/v1/evidence/{evidence_id}/download")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"%PDF-1.4 dummy content"
    assert response.headers["content-type"] == "application/pdf"


def test_delete_evidence(authorized_client, dummy_pdf_file):
    # Upload
    upload_res = authorized_client.post(
        "/api/v1/evidence/",
        data={"judul": "To Be Deleted"},
        files={"file": dummy_pdf_file},
    )
    evidence_id = upload_res.json()["id"]

    # Delete
    delete_res = authorized_client.delete(f"/api/v1/evidence/{evidence_id}")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    # Verify Not Found
    get_res = authorized_client.get(f"/api/v1/evidence/{evidence_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_evidence_forbidden_for_non_uploader(
    client, db, dummy_pdf_file, admin_token, tim_prodi_token, tim_prodi_user
):
    """tim_prodi user should NOT be able to delete evidence uploaded by admin."""
    # Admin uploads
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Admin Uploaded Doc"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(admin_token),
    )
    assert upload_res.status_code == status.HTTP_201_CREATED
    evidence_id = upload_res.json()["id"]

    # tim_prodi tries to delete — should be 403
    delete_res = client.delete(
        f"/api/v1/evidence/{evidence_id}",
        headers=_auth_headers(tim_prodi_token),
    )
    assert delete_res.status_code == status.HTTP_403_FORBIDDEN


def test_delete_evidence_allowed_for_uploader(client, dummy_pdf_file, tim_prodi_token):
    """The user who uploaded the file should be able to delete it themselves."""
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Tim Prodi Own Doc"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(tim_prodi_token),
    )
    assert upload_res.status_code == status.HTTP_201_CREATED
    evidence_id = upload_res.json()["id"]

    delete_res = client.delete(
        f"/api/v1/evidence/{evidence_id}",
        headers=_auth_headers(tim_prodi_token),
    )
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT


# ── EvidenceIndikator linking ────────────────────────────────────────────────


def test_link_evidence_to_indikator(
    client, dummy_pdf_file, admin_token, seeded_indikator_and_target
):
    """Linking an evidence to an indikator should return 201."""
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Evidence to Link"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(admin_token),
    )
    evidence_id = upload_res.json()["id"]
    target = seeded_indikator_and_target["target"]
    indikator = seeded_indikator_and_target["indikator"]

    response = client.post(
        f"/api/v1/evidence/{evidence_id}/indikator",
        json={
            "indikator_id": str(indikator.id),
            "target_akreditasi_id": str(target.id),
        },
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["evidence_id"] == evidence_id
    assert body["indikator_id"] == str(indikator.id)
    assert body["target_akreditasi_id"] == str(target.id)


def test_link_evidence_duplicate_returns_409(
    client, dummy_pdf_file, admin_token, seeded_indikator_and_target
):
    """Linking the same evidence+indikator+target twice should return 409."""
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Duplicate Link Doc"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(admin_token),
    )
    evidence_id = upload_res.json()["id"]
    target = seeded_indikator_and_target["target"]
    indikator = seeded_indikator_and_target["indikator"]

    payload = {
        "indikator_id": str(indikator.id),
        "target_akreditasi_id": str(target.id),
    }
    client.post(
        f"/api/v1/evidence/{evidence_id}/indikator",
        json=payload,
        headers=_auth_headers(admin_token),
    )
    response = client.post(
        f"/api/v1/evidence/{evidence_id}/indikator",
        json=payload,
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_evidence_indikator_links(
    client, dummy_pdf_file, admin_token, seeded_indikator_and_target
):
    """GET /evidence/{id}/indikator should return the list of linked indicators."""
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Evidence with Links"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(admin_token),
    )
    evidence_id = upload_res.json()["id"]
    target = seeded_indikator_and_target["target"]
    indikator = seeded_indikator_and_target["indikator"]

    client.post(
        f"/api/v1/evidence/{evidence_id}/indikator",
        json={
            "indikator_id": str(indikator.id),
            "target_akreditasi_id": str(target.id),
        },
        headers=_auth_headers(admin_token),
    )

    response = client.get(
        f"/api/v1/evidence/{evidence_id}/indikator",
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_200_OK
    links = response.json()
    assert isinstance(links, list)
    assert len(links) == 1
    assert links[0]["indikator_id"] == str(indikator.id)


def test_unlink_evidence_from_indikator(
    client, dummy_pdf_file, admin_token, seeded_indikator_and_target
):
    """DELETE /evidence/{id}/indikator/{indikator_id} should remove the link."""
    upload_res = client.post(
        "/api/v1/evidence/",
        data={"judul": "Evidence to Unlink"},
        files={"file": dummy_pdf_file},
        headers=_auth_headers(admin_token),
    )
    evidence_id = upload_res.json()["id"]
    target = seeded_indikator_and_target["target"]
    indikator = seeded_indikator_and_target["indikator"]

    client.post(
        f"/api/v1/evidence/{evidence_id}/indikator",
        json={
            "indikator_id": str(indikator.id),
            "target_akreditasi_id": str(target.id),
        },
        headers=_auth_headers(admin_token),
    )

    response = client.delete(
        f"/api/v1/evidence/{evidence_id}/indikator/{indikator.id}",
        params={"target_akreditasi_id": str(target.id)},
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    links_res = client.get(
        f"/api/v1/evidence/{evidence_id}/indikator",
        headers=_auth_headers(admin_token),
    )
    assert links_res.json() == []
