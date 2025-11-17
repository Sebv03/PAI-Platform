# backend/app/schemas/user.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole # Importa el Enum de roles

# Esquema base para la creación de un usuario
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.ESTUDIANTE # Valor por defecto, pero se puede especificar
    is_active: Optional[bool] = True

# Esquema para la actualización de un usuario (todos los campos son opcionales)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# Esquema principal para la respuesta del usuario (lo que se devuelve por la API)
class User(BaseModel): # NOTA: Se llama igual que el modelo, pero es el esquema Pydantic
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    role: UserRole # Aquí se espera el Enum de roles

    # Opcional: Si quieres mostrar los IDs de los cursos o inscripciones directamente
    # courses_ids: List[int] = [] # Para IDs de cursos creados
    # enrollment_ids: List[int] = [] # Para IDs de cursos inscritos

    class Config:
        orm_mode = True # Permite que Pydantic lea directamente de un objeto SQLAlchemy
        from_attributes = True # Pydantic v2: Usa from_attributes en lugar de orm_mode