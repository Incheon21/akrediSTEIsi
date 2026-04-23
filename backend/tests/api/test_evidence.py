import io

import pytest
from fastapi import status

# Assuming 'authorized_client' is a fixture provided in conftest.py
# that yields a TestClient authenticated with a test user.


@pytest.fixture
def dummy_pdf_file():
    """Returns a dummy PDF file for upload tests."""
    return ("dummy.pdf", b"%PDF-1.4 dummy content", "application/pdf")


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
