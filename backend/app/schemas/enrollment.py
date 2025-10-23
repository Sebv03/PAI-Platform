# backend/app/schemas/enrollment.py
from pydantic import BaseModel

# Schema para la creación (lo que la API recibe)
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

# Schema para leer (lo que la API devuelve)
class Enrollment(BaseModel):
    id: int
    student_id: int
    course_id: int

    class Config:
        from_attributes = True