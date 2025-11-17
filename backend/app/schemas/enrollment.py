# backend/app/schemas/enrollment.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.schemas.user import User as UserSchema
from app.schemas.course import Course as CourseSchema

# Esquema base para la creación de una inscripción
class EnrollmentCreate(BaseModel):
    # Al crear una inscripción, solo necesitamos el ID del curso.
    # El student_id se obtiene del usuario autenticado.
    course_id: int

# Esquema para la actualización de una inscripción (ej. para un futuro estado)
class EnrollmentUpdate(BaseModel):
    # Campos que se podrían actualizar, si fuera necesario
    pass

# Esquema para la respuesta de una inscripción
class Enrollment(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrollment_date: datetime # La fecha de inscripción

    # Opcional: para incrustar los objetos completos de estudiante y curso
    # student: UserSchema
    # course: CourseSchema

    class Config:
        orm_mode = True
        from_attributes = True