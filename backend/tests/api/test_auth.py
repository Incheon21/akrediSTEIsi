from fastapi.testclient import TestClient


class TestLogin:
    def test_login_success(self, client: TestClient, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password."

    def test_login_wrong_email(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "testpassword123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password."

    def test_login_invalid_email_format(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "testpassword123"},
        )
        assert response.status_code == 422

    def test_login_missing_fields(self, client: TestClient):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_inactive_user(self, client: TestClient, db, seeded_roles):
        from app.core.security import hash_password
        from app.models.user import User

        inactive = User(
            email="inactive@test.com",
            hashed_password=hash_password("testpassword123"),
            nama="Inactive User",
            role_id=seeded_roles["tim_prodi"].id,
            is_active=False,
        )
        db.add(inactive)
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@test.com", "password": "testpassword123"},
        )
        assert response.status_code == 401


class TestMe:
    def test_me_success(self, client: TestClient, admin_token, admin_user):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["nama"] == "Test Admin"
        assert data["is_active"] is True
        assert data["role"]["name"] == "admin"

    def test_me_no_token(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client: TestClient):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 401

    def test_me_wrong_token_type(self, client: TestClient, admin_user):
        # Use refresh token where access token is expected
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "testpassword123"},
        )
        refresh_token = login.json()["refresh_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401

    def test_me_returns_role(self, client: TestClient, tim_prodi_token, tim_prodi_user):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tim_prodi_token}"},
        )
        assert response.status_code == 200
        assert response.json()["role"]["name"] == "tim_prodi"


class TestRefresh:
    def test_refresh_success(self, client: TestClient, admin_user):
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "testpassword123"},
        )
        refresh_token = login.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" not in data

    def test_refresh_with_invalid_token(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalidtoken"},
        )
        assert response.status_code == 401

    def test_refresh_with_access_token(self, client: TestClient, admin_token):
        # Access token should be rejected as a refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": admin_token},
        )
        assert response.status_code == 401
        assert "not a refresh token" in response.json()["detail"]

    def test_refresh_missing_field(self, client: TestClient):
        response = client.post("/api/v1/auth/refresh", json={})
        assert response.status_code == 422

    def test_new_access_token_is_valid(self, client: TestClient, admin_user):
        # Get a new access token via refresh and use it on /me
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "testpassword123"},
        )
        refresh_token = login.json()["refresh_token"]

        refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        new_access_token = refresh.json()["access_token"]

        me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "admin@test.com"
