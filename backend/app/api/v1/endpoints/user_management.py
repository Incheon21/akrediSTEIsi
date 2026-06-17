from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.user import User
from app.models.role import Role
from app.models.program_studi import ProgramStudi
from app.schemas.user_management import (
    GetAllUsersResponse,
    GetAllRolesResponse,
    GetAllProgramStudiResponse,
    UserResponse,
    CreateUserRequest,
    UpdateUserRequest,
)
from app.utils.dependencies import require_role, get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/user-management", tags=["user-management"])

_ADMIN = Depends(require_role("admin"))

@router.get(
    "/users",
    response_model=GetAllUsersResponse,
    summary="Get all users",
    dependencies=[_ADMIN],
)
def get_all_users(db: Session = Depends(get_db)) -> GetAllUsersResponse:
    """Mengembalikan data seluruh user."""
    users = db.execute(select(User)).scalars().all()
    return GetAllUsersResponse.model_validate({"users": users})


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    dependencies=[_ADMIN],
)
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserResponse:
    """Mengembalikan data user berdasarkan ID."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")
    return UserResponse.model_validate(user)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[_ADMIN],
)
def create_user(body: CreateUserRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Membuat user baru."""
    existing_email = db.execute(
        select(User).where(User.email == body.email)
    ).scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah digunakan")

    if body.nip:
        existing_nip = db.execute(
            select(User).where(User.nip == body.nip)
        ).scalar_one_or_none()
        if existing_nip:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIP sudah digunakan")

    role = db.get(Role, body.role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role tidak ditemukan")

    if role.name in ["admin", "pimpinan"]:
        if body.program_studi_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role.name}' tidak dapat dihubungkan dengan Program Studi."
            )

    if body.program_studi_id:
        prodi = db.get(ProgramStudi, body.program_studi_id)
        if not prodi:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program studi tidak ditemukan")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        nama=body.nama,
        nip=body.nip,
        is_active=body.is_active,
        role_id=body.role_id,
        program_studi_id=body.program_studi_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    dependencies=[_ADMIN],
)
def update_user(
    user_id: UUID, body: UpdateUserRequest, db: Session = Depends(get_db)
) -> UserResponse:
    """Memperbarui data user."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    if body.email is not None and body.email != user.email:
        existing = db.execute(
            select(User).where(User.email == body.email)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah digunakan")
        user.email = body.email

    if body.nip is not None and body.nip != "" and body.nip != user.nip:
        existing = db.execute(
            select(User).where(User.nip == body.nip)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="NIP sudah digunakan")
        user.nip = body.nip

    if body.nama is not None:
        user.nama = body.nama

    if body.password is not None:
        user.hashed_password = hash_password(body.password)

    if body.is_active is not None:
        user.is_active = body.is_active

    if body.role_id is not None:
        role = db.get(Role, body.role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role tidak ditemukan")
        user.role_id = body.role_id

    # Enforce program_studi_id = None for global roles
    current_role = db.get(Role, user.role_id)
    if current_role and current_role.name in ["admin", "pimpinan"]:
        if body.program_studi_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{current_role.name}' tidak dapat dihubungkan dengan Program Studi."
            )
        user.program_studi_id = None

    if body.program_studi_id is not None:
        prodi = db.get(ProgramStudi, body.program_studi_id)
        if not prodi:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program studi tidak ditemukan")
        user.program_studi_id = body.program_studi_id

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[_ADMIN],
)
def delete_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda tidak dapat menghapus akun Anda sendiri"
        )
        
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")
    db.delete(user)
    db.commit()

@router.get(
    "/roles",
    response_model=GetAllRolesResponse,
    summary="Get all roles",
    dependencies=[_ADMIN],
)
def get_all_roles(db: Session = Depends(get_db)) -> GetAllRolesResponse:
    """Mengembalikan semua role yang tersedia."""
    roles = db.execute(select(Role)).scalars().all()
    return GetAllRolesResponse.model_validate({"roles": roles})

@router.get(
    "/program-studi",
    response_model=GetAllProgramStudiResponse,
    summary="Get all program studi",
    dependencies=[_ADMIN],
)
def get_all_program_studi(db: Session = Depends(get_db)) -> GetAllProgramStudiResponse:
    """Mengembalikan semua program studi yang tersedia."""
    program_studi = db.execute(select(ProgramStudi)).scalars().all()
    return GetAllProgramStudiResponse.model_validate({"program_studi": program_studi})
