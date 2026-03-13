from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# TODO: move access config to database
ROLE_PERMISSIONS = {
    "admin": ["/dashboard", "/users/create"],
    "user": ["/dashboard"],
}

class RBACMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        if request.url.path in ["/open", "/login"]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing or invalid Authorization header"}, status_code=401)
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            if role is None:
                return JSONResponse({"detail": "Role missing in token"}, status_code=403)
            
            allowed_paths = ROLE_PERMISSIONS.get(role, [])
            if request.url.path not in allowed_paths:
                return JSONResponse({"detail": "You do not have permission to access this resource"}, status_code=403)

            request.state.user = payload

        except JWTError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        response = await call_next(request)
        return response
