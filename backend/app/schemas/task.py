# backend/app/schemas/task.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Propiedades comunes que una tarea puede tener
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime # La fecha de entrega de la tarea
    course_id: int # ID del curso al que pertenece la tarea

# Propiedades para la creación de una tarea (cuando el usuario envía datos)
class TaskCreate(TaskBase):
    pass # No hay propiedades adicionales requeridas para la creación en este momento

# Propiedades para la actualización de una tarea (algunos campos son opcionales)
class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    course_id: Optional[int] = None # Aunque un course_id no suele cambiar, lo dejamos opcional

# Propiedades que la API devuelve (incluye campos generados por la BD)
class Task(TaskBase):
    id: int
    created_at: datetime # Fecha de creación de la tarea (generada por la BD)

    # Configuración para que Pydantic pueda leer modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)