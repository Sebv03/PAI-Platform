# backend/app/api/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import get_db # Importa get_db desde session
from app.models.user import User
from app.schemas.token import TokenPayload
from app.crud import crud_user # Importamos crud_user

# Usamos la ruta correcta de tu login.py
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token" 
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="No se pudieron validar las credenciales (token inválido o expirado)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # --- ¡AÑADE ESTAS LÍNEAS DE DEPURACIÓN! ---
        print(f"\n--- Depuración de Token ---")
        print(f"Token recibido: {token}")
        print(f"Payload decodificado: {payload}")
        print(f"ID de usuario (token_data.sub): {token_data.sub}")
        print(f"Tipo de token_data.sub: {type(token_data.sub)}")
        print(f"---------------------------\n")
        # -------------------------------------------

    except (jwt.JWTError, ValidationError) as e:
        print(f"Error al decodificar o validar el token: {e}") # Añade este print también
        raise credentials_exception
    
    user = crud_user.get_user_by_id(db, user_id=token_data.sub) 
    
    if not user:
        print(f"Usuario con ID {token_data.sub} NO encontrado en la BD.") # Depuración
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# (El resto de las dependencias de roles como get_current_active_admin_user
#  funcionarán correctamente si dependen de get_current_active_user)

def get_current_active_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin": # Ajusta "admin" a tu Enum si es necesario
        raise HTTPException(
            status_code=403, detail="El usuario no tiene permisos de administrador"
        )
    return current_user

def get_current_active_docente_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "docente": # Ajusta "docente" a tu Enum
        raise HTTPException(
            status_code=403, detail="El usuario no tiene permisos de docente"
        )
    return current_user