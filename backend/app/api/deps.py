# backend/app/api/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings # ¡Importamos settings!
from app.db.session import get_db
from app.models.user import User, UserRole # Importamos User y UserRole (del modelo)
from app.schemas.token import TokenPayload # token_data.sub: Optional[int] = None
from app.crud import crud_user

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
    
    # Validar que el token tenga el formato correcto antes de intentar decodificarlo
    if not token or not isinstance(token, str):
        print(f"DEBUG: Token inválido o vacío recibido. Tipo: {type(token)}, Valor: {token}")
        raise credentials_exception
    
    # Limpiar el token (eliminar espacios en blanco)
    token = token.strip()
    
    # Verificar que el token tenga el formato JWT correcto (3 segmentos separados por puntos)
    token_parts = token.split('.')
    if len(token_parts) != 3:
        print(f"DEBUG: Token con formato incorrecto. Segmentos: {len(token_parts)}, Token (primeros 50 chars): {token[:50]}...")
        raise credentials_exception
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Validar que el payload tenga el campo 'sub'
        if "sub" not in payload:
            print(f"DEBUG: El token no contiene el campo 'sub'. Payload: {payload}")
            raise credentials_exception
        
        # Convertir 'sub' a int si es necesario (puede venir como string)
        sub_value = payload.get("sub")
        if isinstance(sub_value, str):
            try:
                sub_value = int(sub_value)
            except ValueError:
                print(f"DEBUG: El campo 'sub' no es un número válido: {sub_value}")
                raise credentials_exception
        
        # Crear TokenPayload con el valor convertido
        token_data = TokenPayload(sub=sub_value)
        
    except jwt.ExpiredSignatureError:
        print("DEBUG: El token ha expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        print(f"DEBUG: Error JWT al decodificar el token: {type(e).__name__}: {e}")
        raise credentials_exception
    except ValidationError as e:
        print(f"DEBUG: Error de validación Pydantic: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"DEBUG: Error inesperado al validar el token: {type(e).__name__}: {e}")
        raise credentials_exception
    
    # --- ¡CRÍTICO! Buscamos al usuario por ID ---
    if token_data.sub is None:
        print("DEBUG: token_data.sub es None")
        raise credentials_exception
    
    user = crud_user.get_user_by_id(db, user_id=token_data.sub) 
    
    if not user:
        # AÑADIMOS UN PRINT PARA DEPURACIÓN. SI VES ESTO, EL ID DEL TOKEN NO EXISTE EN LA BD
        print(f"DEBUG: Token válido, pero usuario con ID {token_data.sub} NO encontrado en la BD.")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    # --- ¡CRÍTICO! Eliminamos el chequeo de 'is_superuser' aquí ---
    return current_user

# --- Dependencias de roles específicas (usando el campo 'role') ---

def get_current_active_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=403, detail="El usuario no tiene permisos de administrador"
        )
    return current_user

def get_current_active_docente_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.DOCENTE:
        raise HTTPException(
            status_code=403, detail="El usuario no tiene permisos de docente"
        )
    return current_user

# Puedes añadir más para Psicopedagogo, etc.