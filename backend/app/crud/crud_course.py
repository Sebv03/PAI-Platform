# backend/app/crud/crud_course.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.course import Course # Asegúrate de importar el modelo Course
from app.models.user import User # Necesario para crear un curso asociado a un usuario
from app.schemas.course import CourseCreate, CourseUpdate # Necesario para los esquemas

# ----------------- Obtener todos los cursos -----------------
def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """
    Obtiene una lista de todos los cursos.
    """
    return db.query(Course).offset(skip).limit(limit).all()

# ----------------- Obtener un curso por ID -----------------
def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
    """
    Obtiene un curso específico por su ID.
    """
    return db.query(Course).filter(Course.id == course_id).first()

# ----------------- Obtener cursos por propietario (docente) -----------------
def get_courses_by_owner(db: Session, owner_id: int) -> List[Course]:
    """
    Obtiene todos los cursos creados por un propietario (docente) específico.
    """
    return db.query(Course).filter(Course.owner_id == owner_id).all()

# ----------------- Crear un curso para un usuario (docente) -----------------
def create_user_course(db: Session, course_in: CourseCreate, owner: User) -> Course:
    """
    Crea un nuevo curso y lo asocia a un usuario propietario.
    """
    db_course = Course(
        title=course_in.title,
        description=course_in.description,
        subject=course_in.subject,  # Asignatura opcional
        paes_topic=course_in.paes_topic,  # Temática PAES opcional
        owner_id=owner.id # Asocia el curso al ID del propietario
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# ----------------- Actualizar un curso existente -----------------
def update_course(db: Session, db_obj: Course, obj_in: CourseUpdate) -> Course:
    """
    Actualiza un curso existente en la base de datos.
    """
    for field in obj_in.model_dump(exclude_unset=True): # Usa model_dump para Pydantic v2
        setattr(db_obj, field, getattr(obj_in, field))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# ----------------- Eliminar un curso existente -----------------
def delete_course(db: Session, id: int) -> Optional[Course]:
    """
    Elimina un curso específico por su ID.
    """
    db_course = db.query(Course).filter(Course.id == id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
    return db_course

# ----------------- Obtener cursos disponibles para un estudiante (no inscritos) -----------------
def get_available_courses_for_student(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
    """
    Obtiene la lista de cursos a los que un estudiante NO está inscrito.
    Excluye los cursos que el estudiante ya tiene inscritos.
    """
    from app.models.enrollment import Enrollment
    
    # Obtener los IDs de cursos en los que el estudiante ya está inscrito
    enrolled_enrollments = db.query(Enrollment.course_id).filter(
        Enrollment.student_id == student_id
    ).all()
    
    enrolled_course_ids = [enrollment[0] for enrollment in enrolled_enrollments]
    
    # Si no hay cursos inscritos, devolver todos los cursos
    if not enrolled_course_ids:
        return db.query(Course).offset(skip).limit(limit).all()
    
    # Query principal: Todos los cursos excepto los ya inscritos
    return db.query(Course).filter(
        ~Course.id.in_(enrolled_course_ids)
    ).offset(skip).limit(limit).all()