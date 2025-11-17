# backend/app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_user
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.models.user import User # <-- ¡AQUÍ ESTÁ TU MODELO User de SQLAlchemy!

router = APIRouter()

# ----------------- Endpoint para crear un usuario -----------------
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Crea un nuevo usuario en la base de datos.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )
    user = crud_user.create_user(db, user_in=user_in)
    return user

# ----------------- Endpoint para obtener el usuario actual -----------------
@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(deps.get_current_user), # <-- ¡CORREGIDO AQUÍ!
) -> Any:
    """
    Obtiene los detalles del usuario autenticado actualmente.
    """
    return current_user

# ----------------- Endpoint para obtener un usuario por ID (Solo Admin) -----------------
@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # <-- ¡Y AQUÍ!
) -> Any:
    """
    Obtiene un usuario por su ID (solo accesible por administradores o el propio usuario).
    """
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    
    if current_user.id == user_id or current_user.role == User.UserRole.ADMINISTRADOR: # <-- Acceso a UserRole
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para acceder a este usuario."
    )

# ----------------- Endpoint para obtener todos los usuarios (Solo Admin) -----------------
@router.get("/", response_model=List[UserSchema])
async def read_all_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user) # <-- ¡Y AQUÍ!
) -> Any:
    """
    Obtiene una lista de todos los usuarios (solo para administradores).
    """
    if current_user.role != User.UserRole.ADMINISTRADOR: # <-- Acceso a UserRole
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver todos los usuarios."
        )
    
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users