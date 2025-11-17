# backend/app/api/endpoints/login.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.crud_user import authenticate_user # Asegúrate que esto esté importado
from app.schemas.token import Token # Asegúrate que esto esté importado
from datetime import timedelta # Asegúrate que esto esté importado

router = APIRouter()

@router.post("/access-token", response_model=Token)
async def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email o contraseña incorrectos"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.id}, # <--- ¡IMPORTANTE! El SUB es el ID del usuario
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }