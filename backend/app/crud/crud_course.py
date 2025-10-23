# backend/app/crud/crud_course.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate

def create_user_course(
    db: Session, *, course_in: CourseCreate, owner: User
) -> Course:
    """
    Crea un nuevo curso en la base de datos propiedad de un usuario.
    """
    # Convertimos el schema Pydantic a un diccionario
    course_data = course_in.model_dump()

    # Creamos la instancia del modelo SQLAlchemy
    db_course = Course(**course_data, owner=owner) # ¡Aquí asignamos el propietario!

    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return db_course

# ... al final de crud_course.py
from app.models.course import Course # Asegúrate que Course esté importado

def get_course_by_id(db: Session, *, course_id: int) -> Course | None:
    """
    Busca un curso por su ID.
    """
    return db.query(Course).filter(Course.id == course_id).first()

def get_courses(
    db: Session,
    owner_id: Optional[int] = None, # <-- NUEVO PARÁMETRO
    skip: int = 0,
    limit: int = 100
) -> List[Course]:
    """
    Obtiene una lista de cursos.
    Si se proporciona owner_id, filtra los cursos por ese propietario.
    """
    query = db.query(Course)
    if owner_id:
        query = query.filter(Course.owner_id == owner_id) # <-- FILTRADO
    return query.offset(skip).limit(limit).all()