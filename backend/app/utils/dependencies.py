from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session, joinedload
import json

from app.core.security import decode_token
from app.db import get_db
from app.models.user import User
from app.services.auth import get_user_by_id

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the Bearer token from the
    Authorization header, then returns the corresponding active User.

    Raises HTTP 401 if the token is missing, invalid, or expired.
    Raises HTTP 403 if the user account is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = json.loads(payload.get("sub")).get("user_id")
    if user_id is None:
        raise credentials_exception

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == UUID(user_id))
        .first()
    )
    if user is None:
        raise credentials_exception

    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


def require_role(*role_names: str):
    """
    Dependency factory that restricts access to users whose role name
    matches one of the provided role names.

    Usage:
        @router.get("/admin-only")
        def admin_only(current_user: User = Depends(require_role("admin"))):
            ...
    """

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role is None or current_user.role.name not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Required role(s): {', '.join(role_names)}.",
            )
        return current_user

    return _check


def get_current_admin(
    current_user: User = Depends(require_role("admin")),
) -> User:
    """Shorthand dependency for admin-only routes."""
    return current_user


def get_global_access_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that restricts access to users with global (multi-prodi) access:
    admin, pimpinan, and koordinator.
    tim_prodi users are scoped to their own prodi and are rejected here.
    """
    global_roles = {"admin", "pimpinan", "koordinator"}
    if current_user.role is None or current_user.role.name not in global_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Global access required.",
        )
    return current_user
