from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db import SessionLocal
from app.models.role_access import RoleAccess


class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # Public endpoints
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header"},
                status_code=401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)

            role_id = payload.get("role_id")
            if role_id is None:
                return JSONResponse(
                    {"detail": "Role missing in token"},
                    status_code=403,
                )

            path = request.url.path
            method = request.method

            db: Session = SessionLocal()

            permission = (
                db.query(RoleAccess)
                .filter(
                    RoleAccess.role_id == role_id,
                    RoleAccess.api_path == path,
                    RoleAccess.http_method == method,
                )
                .first()
            )

            db.close()

            if permission is None:
                return JSONResponse(
                    {"detail": "You do not have permission to access this resource"},
                    status_code=403,
                )

            # Attach user info to request
            request.state.user = payload

        except Exception:
            return JSONResponse(
                {"detail": "Invalid token"},
                status_code=401,
            )

        return await call_next(request)
