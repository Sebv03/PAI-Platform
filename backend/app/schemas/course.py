# backend/app/schemas/course.py
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import User as UserSchema # Importa el esquema de User para anidarlo

# Esquema base para la creación de un curso
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None # La descripción puede ser opcional al crear

# Esquema para la actualización de un curso
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

# Esquema principal para la respuesta del curso (lo que se devuelve por la API)
class Course(BaseModel): # NOTA: Se llama igual que el modelo, pero es el esquema Pydantic
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int # El ID del propietario
    owner_name: Optional[str] = None  # Nombre del profesor
    owner_email: Optional[str] = None  # Email del profesor
    created_at: Optional[str] = None  # Fecha de creación

    # Opcional: Para incluir el objeto completo del propietario si se desea en algunas respuestas
    # owner: UserSchema # Descomentar si quieres incrustar el objeto User completo

    class Config:
        orm_mode = True # Permite que Pydantic lea directamente de un objeto SQLAlchemy
        from_attributes = True # Pydantic v2: Usa from_attributes en lugar de orm_mode