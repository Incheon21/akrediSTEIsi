from uuid import UUID

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import AccessTokenResponse, TokenResponse


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify email + password combination.
    Returns the User on success, None on failure.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    if not bool(user.is_active):
        return None
    return user


def create_tokens_for_user(user: User) -> TokenResponse:
    """Issue a fresh access + refresh token pair for a given user."""
    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_refresh_token(subject=str(user.id)),
    )


def refresh_access_token(db: Session, refresh_token: str) -> AccessTokenResponse:
    """
    Validate a refresh token and issue a new access token.
    Raises ValueError if the token is invalid, expired, or not a refresh token.
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise ValueError("Invalid or expired refresh token.")

    if payload.get("type") != "refresh":
        raise ValueError("Provided token is not a refresh token.")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise ValueError("Token payload is missing subject.")

    user = get_user_by_id(db, UUID(user_id))
    if user is None or not bool(user.is_active):
        raise ValueError("User not found or inactive.")

    return AccessTokenResponse(access_token=create_access_token(subject=str(user.id)))
