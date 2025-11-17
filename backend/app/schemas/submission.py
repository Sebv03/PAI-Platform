# backend/app/schemas/submission.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Campos que se comparten (base)
class SubmissionBase(BaseModel):
    content: Optional[str] = None

# Esquema para crear una entrega (lo que envía el estudiante)
# El student_id vendrá del token
# El task_id vendrá de la URL
class SubmissionCreate(SubmissionBase):
    pass # Solo necesita el contenido

# Esquema para actualizar (ej. un docente añade nota)
class SubmissionUpdate(BaseModel):
    content: Optional[str] = None
    # Añadiremos 'grade' y 'feedback' aquí cuando creemos el modelo Grade

# Esquema para leer una entrega (lo que la API devuelve)
class Submission(SubmissionBase):
    id: int
    student_id: int
    task_id: int
    submitted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)