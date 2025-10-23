# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from app.core.config import settings

# 1. Contexto para el hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Esquema de seguridad OAuth2
# Le dice a FastAPI dónde buscar el token (en la cabecera 'Authorization: Bearer TOKEN')
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/token")

# 3. Función de verificación
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 4. Función de hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 5. Función de creación de token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt