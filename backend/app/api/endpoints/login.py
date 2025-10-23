# backend/app/api/endpoints/login.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# --- CORRECCIÓN AQUÍ ---
# Importamos la clase Token directamente desde su archivo.
from app.schemas.token import Token
# -------------------------

from app.crud import crud_user
from app.api import deps
from app.core.config import settings
from app.core import security

router = APIRouter()

# --- Y CORRECCIÓN AQUÍ ---
# Usamos 'Token' directamente en el response_model.
@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Obtiene un token de acceso JWT.
    """
    user = crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}