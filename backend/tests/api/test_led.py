import uuid

from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.narasi_led import NarasiLED
from app.models.program_studi import ProgramStudi
from app.models.role import Role
from app.models.target_akreditasi import TargetAkreditasi
from app.models.user import User


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _seed_led_context(db, tim_prodi_user: User):
    """
    Seed minimal relational data needed by LED endpoints:
    ProgramStudi -> TargetAkreditasi, Kriteria -> Indikator, and user-prodi linkage.
    """
    # Ensure tim_prodi user is attached to a program studi
    if tim_prodi_user.program_studi_id is None:
        prodi = ProgramStudi(
            kode=f"IF-{uuid.uuid4().hex[:6]}",
            nama="Teknik Informatika Test",
            jenjang="S1",
            fakultas="STEI",
            status="aktif",
        )
        db.add(prodi)
        db.flush()

        tim_prodi_user.program_studi_id = prodi.id
        db.add(tim_prodi_user)
        db.flush()
    else:
        prodi = (
            db.query(ProgramStudi)
            .filter(ProgramStudi.id == tim_prodi_user.program_studi_id)
            .first()
        )
        if prodi is None:
            prodi = ProgramStudi(
                id=tim_prodi_user.program_studi_id,
                kode=f"IF-{uuid.uuid4().hex[:6]}",
                nama="Teknik Informatika Test",
                jenjang="S1",
                fakultas="STEI",
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
        nama="Kriteria Test LED",
    )
    db.add(kriteria)
    db.flush()

    indikator = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-{uuid.uuid4().hex[:6]}",
        deskripsi="Deskripsi indikator test",
        tipe_input="teks",
    )
    db.add(indikator)
    db.commit()
    db.refresh(target)
    db.refresh(indikator)

    return {
        "prodi": prodi,
        "target": target,
        "indikator": indikator,
    }


def test_create_narasi_led_success(client, db, tim_prodi_user, tim_prodi_token):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Narasi LED awal",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Narasi LED berhasil disimpan."
    assert body["data"]["target_akreditasi_id"] == str(target.id)
    assert body["data"]["indikator_id"] == str(indikator.id)
    assert body["data"]["narasi"] == "Narasi LED awal"

    row = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target.id,
            NarasiLED.indikator_id == indikator.id,
        )
        .first()
    )
    assert row is not None
    assert row.narasi == "Narasi LED awal"


def test_update_narasi_led_upsert_success(client, db, tim_prodi_user, tim_prodi_token):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    # First save
    first_payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Versi pertama",
    }
    r1 = client.post(
        "/api/v1/led/narasi",
        json=first_payload,
        headers=_auth_headers(tim_prodi_token),
    )
    assert r1.status_code == 200

    first_row = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target.id,
            NarasiLED.indikator_id == indikator.id,
        )
        .first()
    )
    assert first_row is not None
    first_id = first_row.id

    # Second save should update same row
    second_payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Versi kedua (updated)",
    }
    r2 = client.post(
        "/api/v1/led/narasi",
        json=second_payload,
        headers=_auth_headers(tim_prodi_token),
    )
    assert r2.status_code == 200

    rows = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target.id,
            NarasiLED.indikator_id == indikator.id,
        )
        .all()
    )
    assert len(rows) == 1
    assert rows[0].id == first_id
    assert rows[0].narasi == "Versi kedua (updated)"


def test_save_narasi_led_reject_empty_narasi(
    client, db, tim_prodi_user, tim_prodi_token
):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "   ",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Narasi LED tidak boleh kosong."


def test_get_narasi_led_success(client, db, tim_prodi_user, tim_prodi_token):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    created = NarasiLED(
        target_akreditasi_id=target.id,
        indikator_id=indikator.id,
        narasi="Narasi untuk GET endpoint",
    )
    db.add(created)
    db.commit()

    response = client.get(
        f"/api/v1/led/narasi?target_akreditasi_id={target.id}&indikator_id={indikator.id}",
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["target_akreditasi_id"] == str(target.id)
    assert body["indikator_id"] == str(indikator.id)
    assert body["narasi"] == "Narasi untuk GET endpoint"


def test_tim_prodi_forbidden_other_prodi_target(
    client, db, tim_prodi_user, tim_prodi_token
):
    """
    tim_prodi should not be able to write LED narasi for target from another prodi.
    """
    own = _seed_led_context(db, tim_prodi_user)
    indikator = own["indikator"]

    other_prodi = ProgramStudi(
        kode=f"EL-{uuid.uuid4().hex[:6]}",
        nama="Teknik Elektro Test",
        jenjang="S1",
        fakultas="STEI",
        status="aktif",
    )
    db.add(other_prodi)
    db.flush()

    other_target = TargetAkreditasi(
        program_studi_id=other_prodi.id,
        tahun_akreditasi=2031,
        target_skor=3.2,
        is_aktif=True,
        notifikasi_aktif=True,
    )
    db.add(other_target)
    db.commit()
    db.refresh(other_target)

    payload = {
        "target_akreditasi_id": str(other_target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Tidak boleh diakses tim_prodi lain",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Anda tidak memiliki akses ke target akreditasi ini."
    )


def test_admin_can_write_any_target(client, db, tim_prodi_user, admin_token):
    """
    admin should be allowed to write narasi for any prodi target.
    """
    seeded = _seed_led_context(db, tim_prodi_user)
    indikator = seeded["indikator"]

    unrelated_prodi = ProgramStudi(
        kode=f"MA-{uuid.uuid4().hex[:6]}",
        nama="Matematika Test",
        jenjang="S1",
        fakultas="MIPA",
        status="aktif",
    )
    db.add(unrelated_prodi)
    db.flush()

    unrelated_target = TargetAkreditasi(
        program_studi_id=unrelated_prodi.id,
        tahun_akreditasi=2032,
        target_skor=3.8,
        is_aktif=True,
        notifikasi_aktif=True,
    )
    db.add(unrelated_target)
    db.commit()
    db.refresh(unrelated_target)

    payload = {
        "target_akreditasi_id": str(unrelated_target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Admin boleh simpan di target mana pun",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["target_akreditasi_id"] == str(unrelated_target.id)
    assert body["data"]["indikator_id"] == str(indikator.id)
    assert body["data"]["narasi"] == "Admin boleh simpan di target mana pun"


def test_led_post_unauthorized_without_token(client, db, tim_prodi_user):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Should fail without token",
    }

    response = client.post("/api/v1/led/narasi", json=payload)

    assert response.status_code == 401
    detail = str(response.json().get("detail", "")).lower()
    assert "not authenticated" in detail or "could not validate credentials" in detail


def test_led_get_unauthorized_without_token(client, db, tim_prodi_user):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    response = client.get(
        f"/api/v1/led/narasi?target_akreditasi_id={target.id}&indikator_id={indikator.id}"
    )

    assert response.status_code == 401
    detail = str(response.json().get("detail", "")).lower()
    assert "not authenticated" in detail or "could not validate credentials" in detail


def test_led_post_target_not_found(client, db, tim_prodi_token):
    kriteria = Kriteria(
        kode=f"C-{uuid.uuid4().hex[:4]}",
        nama="Kriteria Not Found Target",
    )
    db.add(kriteria)
    db.flush()

    indikator = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-{uuid.uuid4().hex[:6]}",
        deskripsi="Indikator valid untuk target tidak ditemukan",
        tipe_input="teks",
    )
    db.add(indikator)
    db.commit()
    db.refresh(indikator)

    payload = {
        "target_akreditasi_id": str(uuid.uuid4()),
        "indikator_id": str(indikator.id),
        "narasi": "Narasi apa pun",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Target akreditasi tidak ditemukan."


def test_led_post_indikator_not_found(client, db, tim_prodi_user, tim_prodi_token):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]

    payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(uuid.uuid4()),
        "narasi": "Narasi apa pun",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Indikator tidak ditemukan."


def test_led_get_not_found_when_narasi_absent(
    client, db, tim_prodi_user, tim_prodi_token
):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    response = client.get(
        f"/api/v1/led/narasi?target_akreditasi_id={target.id}&indikator_id={indikator.id}",
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Narasi LED belum tersedia untuk indikator ini."


def test_led_get_indikator_not_found(client, db, tim_prodi_user, tim_prodi_token):
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]

    response = client.get(
        f"/api/v1/led/narasi?target_akreditasi_id={target.id}&indikator_id={uuid.uuid4()}",
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Indikator tidak ditemukan."


def test_led_get_target_not_found(client, tim_prodi_token):
    response = client.get(
        f"/api/v1/led/narasi?target_akreditasi_id={uuid.uuid4()}&indikator_id={uuid.uuid4()}",
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Target akreditasi tidak ditemukan."


def test_led_post_rejected_for_unallowed_role(client, db):
    role = db.query(Role).filter(Role.name == "reviewer").first()
    if role is None:
        role = Role(name="reviewer")
        db.add(role)
        db.flush()

    user = db.query(User).filter(User.email == "reviewer@test.com").first()
    if user is None:
        from app.core.security import hash_password

        user = User(
            email="reviewer@test.com",
            hashed_password=hash_password("testpassword123"),
            nama="Reviewer Test",
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "reviewer@test.com", "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    prodi = ProgramStudi(
        kode=f"AR-{uuid.uuid4().hex[:6]}",
        nama="Arsitektur Test",
        jenjang="S1",
        fakultas="SAPPK",
        status="aktif",
    )
    db.add(prodi)
    db.flush()

    target = TargetAkreditasi(
        program_studi_id=prodi.id,
        tahun_akreditasi=2033,
        target_skor=3.0,
        is_aktif=True,
        notifikasi_aktif=True,
    )
    db.add(target)
    db.flush()

    kriteria = Kriteria(
        kode=f"C-{uuid.uuid4().hex[:4]}",
        nama="Kriteria Reviewer Rejection",
    )
    db.add(kriteria)
    db.flush()

    indikator = Indikator(
        kriteria_id=kriteria.id,
        kode_indikator=f"I-{uuid.uuid4().hex[:6]}",
        deskripsi="Indikator untuk uji role rejection",
        tipe_input="teks",
    )
    db.add(indikator)
    db.commit()
    db.refresh(target)
    db.refresh(indikator)

    payload = {
        "target_akreditasi_id": str(target.id),
        "indikator_id": str(indikator.id),
        "narasi": "Seharusnya ditolak karena role tidak diizinkan",
    }

    response = client.post(
        "/api/v1/led/narasi",
        json=payload,
        headers=_auth_headers(token),
    )

    assert response.status_code == 403
    assert "Access restricted." in response.json()["detail"]


def test_export_led_word_success(client, db, tim_prodi_user, tim_prodi_token):
    """
    GET /led/export/{target_akreditasi_id} should return a .docx file
    with the correct content-type when at least one narasi exists.
    """
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]
    indikator = seeded["indikator"]

    # Seed a narasi so the document has content to render
    narasi = NarasiLED(
        target_akreditasi_id=target.id,
        indikator_id=indikator.id,
        narasi="Narasi test untuk export LED Word document.",
    )
    db.add(narasi)
    db.commit()

    response = client.get(
        f"/api/v1/led/export/{target.id}",
        headers=_auth_headers(tim_prodi_token),
    )

    assert response.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        in response.headers["content-type"]
    )
    assert "attachment" in response.headers.get("content-disposition", "")
    # Verify the response body is a non-empty binary (valid docx starts with PK zip magic bytes)
    assert response.content[:2] == b"PK"


def test_export_led_word_not_found(client, tim_prodi_token):
    """GET /led/export/{nonexistent_id} should return 404."""
    import uuid

    response = client.get(
        f"/api/v1/led/export/{uuid.uuid4()}",
        headers=_auth_headers(tim_prodi_token),
    )
    assert response.status_code == 404


def test_export_led_word_unauthorized(client, db, tim_prodi_user):
    """GET /led/export without a token should return 401."""
    seeded = _seed_led_context(db, tim_prodi_user)
    target = seeded["target"]

    response = client.get(f"/api/v1/led/export/{target.id}")
    assert response.status_code == 401
