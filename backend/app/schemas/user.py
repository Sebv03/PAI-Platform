# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.models.user import UserRole # Importa el Enum

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.ESTUDIANTE # Permite especificar el rol al crear

class UserUpdate(BaseModel):
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole # <-- Retorna el rol
    
    model_config = ConfigDict(from_attributes=True) # para Pydantic v2