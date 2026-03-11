from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth import (
    authenticate_user,
    create_tokens_for_user,
    refresh_access_token,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user with their email and password.
    Returns an access token (short-lived) and a refresh token (long-lived).
    """
    user = authenticate_user(db, email=body.email, password=body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_tokens_for_user(user)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Obtain a new access token using a refresh token",
)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> AccessTokenResponse:
    """
    Exchange a valid refresh token for a new access token.
    The refresh token itself is not rotated — the same refresh token remains valid
    until it expires.
    """
    try:
        return refresh_access_token(db, refresh_token=body.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def me(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Returns the profile of the currently authenticated user,
    derived from the Bearer token in the Authorization header.
    """
    return current_user
