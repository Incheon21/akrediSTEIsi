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
def tim_prodi_token(client, tim_prodi_user):
    """Return a valid access token for the tim_prodi user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "timprodi@test.com", "password": "testpassword123"},
    )
    return response.json()["access_token"]
