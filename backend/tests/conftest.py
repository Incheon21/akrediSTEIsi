import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.user import User

# Use a separate in-memory SQLite DB for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def authorized_client(client, admin_token):
    """A TestClient pre-configured with a valid admin Bearer token."""
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


@pytest.fixture()
def authorized_client_pimpinan(client, pimpinan_token):
    """A TestClient pre-configured with a valid pimpinan Bearer token."""
    client.headers.update({"Authorization": f"Bearer {pimpinan_token}"})
    return client


@pytest.fixture()
def authorized_client_tim_prodi(client, tim_prodi_token):
    """A TestClient pre-configured with a valid tim_prodi Bearer token."""
    client.headers.update({"Authorization": f"Bearer {tim_prodi_token}"})
    return client


@pytest.fixture()
def seeded_roles(db):
    """Create all four roles and return them as a dict keyed by name."""
    roles = {}
    for name in ["admin", "pimpinan", "koordinator", "tim_prodi"]:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            db.flush()
        roles[name] = role
    db.commit()
    return roles


@pytest.fixture()
def admin_user(db, seeded_roles):
    """Create and return a test admin user."""
    user = db.query(User).filter(User.email == "admin@test.com").first()
    if not user:
        user = User(
            email="admin@test.com",
            hashed_password=hash_password("testpassword123"),
            nama="Test Admin",
            role_id=seeded_roles["admin"].id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture()
def pimpinan_user(db, seeded_roles):
    """Create and return a test admin user."""
    user = db.query(User).filter(User.email == "pimpinan@test.com").first()
    if not user:
        user = User(
            email="pimpinan@test.com",
            hashed_password=hash_password("testpassword123"),
            nama="test pimpinan",
            role_id=seeded_roles["pimpinan"].id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture()
def tim_prodi_user(db, seeded_roles):
    """Create and return a test tim_prodi user."""
    user = db.query(User).filter(User.email == "timprodi@test.com").first()
    if not user:
        user = User(
            email="timprodi@test.com",
            hashed_password=hash_password("testpassword123"),
            nama="Test Tim Prodi",
            role_id=seeded_roles["tim_prodi"].id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    """Return a valid access token for the admin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def pimpinan_token(client, pimpinan_user):
    """Return a valid access token for the pimpinan user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "pimpinan@test.com", "password": "testpassword123"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def tim_prodi_token(client, tim_prodi_user):
    """Return a valid access token for the tim_prodi user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "timprodi@test.com", "password": "testpassword123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def mock_dashboard_prodi_response():
    return {
        "program_studi_profile": {
            "name": "Informatika",
            "degree": "S1",
            "last_accreditation_status": "A",
            "last_accreditation_year": 2022,
            "is_active_accreditation": True,
        },
        "target_akreditasi_id": "dummy-target-id",
        "lkps_submission_id": "dummy-lkps-id",
        "current_year": 2025,
        "available_years": [2025],
        "criteria_list": [],
        "recommendation_messages": ["Test rekomendasi"],
        "early_warnings": [],
        "score_value": 0.0,
        "target_score": 3.5,
        "deadline": "01 Januari 2025",
        "days_remaining": 10,
        "lkps_percent": 0,
        "led_percent": 0,
        "evidence_percent": 0,
    }


@pytest.fixture
def mock_dashboard_multi_response():
    return {
        "fakultas_summary": {
            "total_prodi": 1,
            "prodi_green": 0,
            "prodi_yellow": 0,
            "prodi_red": 1,
            "avg_lkps_percent": 0.0,
            "avg_led_percent": 0.0,
            "avg_simulation_score": 0.0,
        },
        "prodi_list": [
            {
                "id": "dummy-prodi-id",
                "name": "Informatika",
                "degree": "S1",
                "accreditation_status": "A",
                "accreditation_year": 2022,
                "lkps_percent": 0,
                "led_percent": 0,
                "evidence_percent": 0,
                "simulation_score": 0.0,
                "target_score": 3.5,
                "readiness_status": "red",
                "is_active": True,
                "days_remaining": 10,
            }
        ],
        "current_year": 2025,
        "available_years": [2025],
        "data_prodi": [1],
    }
