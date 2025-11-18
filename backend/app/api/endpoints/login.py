# backend/app/api/endpoints/login.py
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user # Importa get_db y get_current_user desde deps
from app.core import security
from app.core.config import settings
from app.crud.crud_user import authenticate_user
from app.schemas.token import Token
from app.schemas.user import User as UserSchema # Alias para evitar conflicto

router = APIRouter()

@router.post("/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña incorrectos")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # --- ¡CRÍTICO! El 'sub' del token DEBE ser el ID del usuario ---
    access_token = security.create_access_token(
        data={"sub": user.id}, # Aquí se usa user.id
        expires_delta=access_token_expires
    )
    
    # Validar que el token tenga el formato correcto antes de retornarlo
    token_parts = access_token.split('.')
    if len(token_parts) != 3:
        print(f"ERROR: Token generado con formato incorrecto. Segmentos: {len(token_parts)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar el token de acceso"
        )
    
    print(f"DEBUG: Token generado correctamente para usuario {user.id}. Segmentos: {len(token_parts)}")
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para probar si el token funciona
@router.get("/test-token", response_model=UserSchema)
def test_token(
    current_user: UserSchema = Depends(get_current_user)
) -> Any:
    """
    Test access token - Verifica que el token JWT sea válido y retorna el usuario actual
    """
    return current_user