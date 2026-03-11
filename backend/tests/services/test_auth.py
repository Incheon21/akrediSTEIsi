from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.role import Role
from app.models.user import User
from app.services.auth import (
    authenticate_user,
    create_tokens_for_user,
    get_user_by_email,
    get_user_by_id,
    refresh_access_token,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_role(name: str = "admin") -> MagicMock:
    role = MagicMock(spec=Role)
    role.id = uuid4()
    role.name = name
    return role


def make_user(
    email: str = "user@test.com",
    password: str = "testpassword123",
    is_active: bool = True,
    role_name: str = "admin",
) -> MagicMock:
    role = make_role(role_name)
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = email
    user.hashed_password = hash_password(password)
    user.nama = "Test User"
    user.role_id = role.id
    user.role = role
    user.is_active = is_active
    return user


# ---------------------------------------------------------------------------
# security.py unit tests
# ---------------------------------------------------------------------------


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        # bcrypt uses a random salt each time
        hash1 = hash_password("mypassword")
        hash2 = hash_password("mypassword")
        assert hash1 != hash2


class TestJWT:
    def test_access_token_decode(self):
        user_id = str(uuid4())
        token = create_access_token(subject=user_id)
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_refresh_token_decode(self):
        user_id = str(uuid4())
        token = create_refresh_token(subject=user_id)
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_access_and_refresh_tokens_are_different(self):
        user_id = str(uuid4())
        access = create_access_token(subject=user_id)
        refresh = create_refresh_token(subject=user_id)
        assert access != refresh

    def test_invalid_token_raises(self):
        from jose import JWTError

        with pytest.raises(JWTError):
            decode_token("this.is.invalid")


# ---------------------------------------------------------------------------
# services/auth.py unit tests
# ---------------------------------------------------------------------------


class TestGetUserByEmail:
    def test_returns_user_when_found(self):
        user = make_user()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = get_user_by_email(db, "user@test.com")
        assert result == user

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_email(db, "nobody@test.com")
        assert result is None


class TestGetUserById:
    def test_returns_user_when_found(self):
        user = make_user()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = get_user_by_id(db, user.id)
        assert result == user

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_id(db, uuid4())
        assert result is None


class TestAuthenticateUser:
    def test_success(self):
        user = make_user(password="correctpassword")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = authenticate_user(db, "user@test.com", "correctpassword")
        assert result == user

    def test_wrong_password_returns_none(self):
        user = make_user(password="correctpassword")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = authenticate_user(db, "user@test.com", "wrongpassword")
        assert result is None

    def test_user_not_found_returns_none(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = authenticate_user(db, "nobody@test.com", "password")
        assert result is None

    def test_inactive_user_returns_none(self):
        user = make_user(password="correctpassword", is_active=False)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = authenticate_user(db, "user@test.com", "correctpassword")
        assert result is None


class TestCreateTokensForUser:
    def test_returns_token_response(self):
        user = make_user()
        result = create_tokens_for_user(user)
        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"

    def test_access_token_contains_user_id(self):
        user = make_user()
        result = create_tokens_for_user(user)
        payload = decode_token(result.access_token)
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "access"

    def test_refresh_token_contains_user_id(self):
        user = make_user()
        result = create_tokens_for_user(user)
        payload = decode_token(result.refresh_token)
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "refresh"


class TestRefreshAccessToken:
    def test_success(self):
        user = make_user()
        refresh_token = create_refresh_token(subject=str(user.id))

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        result = refresh_access_token(db, refresh_token)
        assert result.access_token
        payload = decode_token(result.access_token)
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "access"

    def test_invalid_token_raises(self):
        db = MagicMock()
        with pytest.raises(ValueError, match="Invalid or expired"):
            refresh_access_token(db, "not.a.valid.token")

    def test_access_token_rejected(self):
        user = make_user()
        access_token = create_access_token(subject=str(user.id))
        db = MagicMock()

        with pytest.raises(ValueError, match="not a refresh token"):
            refresh_access_token(db, access_token)

    def test_inactive_user_raises(self):
        user = make_user(is_active=False)
        refresh_token = create_refresh_token(subject=str(user.id))

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        with pytest.raises(ValueError, match="inactive"):
            refresh_access_token(db, refresh_token)

    def test_missing_user_raises(self):
        user_id = str(uuid4())
        refresh_token = create_refresh_token(subject=user_id)

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="not found"):
            refresh_access_token(db, refresh_token)
