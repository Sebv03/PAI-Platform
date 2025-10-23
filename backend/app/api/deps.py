# backend/app/api/deps.py
from typing import Generator
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import reusable_oauth2, settings # Importamos el esquema y settings
from app.models.user import User # Importamos el modelo User directamente
from app.crud import crud_user # Importamos el módulo crud

def get_db() -> Generator:
    """
    Dependencia que proporciona una sesión de base de datos a un endpoint.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# --- FUNCIÓN MOVIDA AQUÍ ---
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Decodifica el token, extrae el email y devuelve el usuario desde la DB.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Token inválido.")
    except JWTError:
        raise HTTPException(status_code=403, detail="Token inválido o expirado.")
    
    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user