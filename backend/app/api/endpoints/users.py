# backend/app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import User, UserCreate
from app.crud import crud_user

# --- CORRECCIÓN AQUÍ ---
# Importamos 'deps' y 'UserModel'
from app.api import deps
from app.models.user import User as UserModel
# -------------------------

router = APIRouter()

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """
    Crea un nuevo usuario.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado en el sistema.",
        )
    
    user = crud_user.create_user(db, user_in=user_in)
    return user

# --- CORRECCIÓN AQUÍ ---
# El 'Depends' ahora apunta a 'deps.get_current_user'
@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Obtiene el perfil del usuario actual.
    """
    return current_user