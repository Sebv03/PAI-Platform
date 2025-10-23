# backend/app/schemas/course.py
from typing import Optional
from pydantic import BaseModel

class CourseBase(BaseModel):
    # Asegúrate de que el campo sea 'title' y no 'name'
    title: str
    description: Optional[str] = None
    category: Optional[str] = None

class CourseCreate(CourseBase):
    pass # Hereda de CourseBase, así que el 'title' ya está ahí

class Course(CourseBase):
    id: int
    owner_id: int # El ID del usuario que creó el curso

    class Config:
        from_attributes = True # En Pydantic v2, esto reemplaza a orm_mode = True