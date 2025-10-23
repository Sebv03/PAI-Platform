# backend/app/schemas/task.py
from pydantic import BaseModel
from datetime import datetime

# Schema base con los campos comunes
class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime # El endpoint esperará una fecha y hora en formato ISO (ej: "2025-10-30T23:59:00Z")

# Schema para la creación (lo que la API recibe)
class TaskCreate(TaskBase):
    pass # Por ahora, es igual al base

# Schema para leer (lo que la API devuelve)
class Task(TaskBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True