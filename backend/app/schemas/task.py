# backend/app/schemas/task.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Esquema Base con campos comunes para Pydantic (sin ID, created_at, etc.)
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime

# Esquema para crear una tarea (incluye course_id, que se envía al crear)
class TaskCreate(TaskBase):
    course_id: int # ¡Este campo es fundamental para la creación!

# Esquema para actualizar una tarea (todos los campos son opcionales)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    # course_id no se suele cambiar una vez creada la tarea, por eso no lo incluimos aquí.

# Esquema para representar una tarea completa (lo que la API devuelve)
class Task(TaskBase):
    id: int
    course_id: int # Confirmamos que se devuelve el ID del curso
    created_at: datetime

    # Configuración para que Pydantic pueda leer modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)