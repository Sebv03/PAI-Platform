# backend/app/schemas/submission.py
from pydantic import BaseModel
from datetime import datetime

# Schema para la creación (lo que la API recibe)
class SubmissionCreate(BaseModel):
    content: str | None = None # El texto de la entrega

# Schema para leer (lo que la API devuelve)
class Submission(BaseModel):
    id: int
    timestamp_entrega: datetime
    content: str | None = None
    task_id: int
    student_id: int

    class Config:
        from_attributes = True