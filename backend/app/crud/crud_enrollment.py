from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.enrollment import Enrollment # Importa el modelo de la BD
from app.models.course import Course # Importa el modelo Course para la función join
from app.models.user import User # Importa el modelo User
from app.schemas.enrollment import EnrollmentCreate # Importa el esquema Pydantic

# ----------------- Obtener una inscripción específica (para verificar si ya existe) -----------------
def get_enrollment_by_user_and_course(db: Session, *, student_id: int, course_id: int) -> Optional[Enrollment]:
    """
    Verifica si un estudiante (user_id) ya está inscrito en un curso (course_id).
    Devuelve el objeto Enrollment si existe, o None si no.
    """
    return db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id == course_id
    ).first()

# ----------------- Crear una nueva inscripción -----------------
def create_enrollment(db: Session, *, student_id: int, course_id: int) -> Enrollment:
    """
    Inscribe a un estudiante en un curso.
    Recibe los IDs directamente (el student_id vendrá del token en el endpoint).
    """
    # Crea el objeto del modelo SQLAlchemy
    db_enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id
        # 'enrollment_date' será generado automáticamente por el server_default=text("NOW()")
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

# ----------------- Obtener cursos en los que un estudiante está inscrito -----------------
def get_enrolled_courses_by_student(db: Session, student_id: int) -> List[Course]:
    """
    Obtiene la lista de Cursos (el objeto Course completo) en los que un estudiante está inscrito.
    """
    # Hacemos un Join: Buscamos Cursos, los unimos con Enrollments,
    # y filtramos donde el Enrollment.student_id coincida.
    return db.query(Course).join(Enrollment).filter(Enrollment.student_id == student_id).all()

# ----------------- Obtener estudiantes inscritos en un curso (Para Docentes) -----------------
def get_students_enrolled_in_course(db: Session, course_id: int) -> List[User]:
    """
    Obtiene la lista de Estudiantes (el objeto User completo) inscritos en un curso específico.
    """
    # Hacemos un Join: Buscamos Usuarios, los unimos con Enrollments,
    # y filtramos donde el Enrollment.course_id coincida.
    return db.query(User).join(Enrollment).filter(Enrollment.course_id == course_id).all()

# ----------------- Eliminar una inscripción (Darse de baja) -----------------
def delete_enrollment(db: Session, db_enrollment: Enrollment) -> Enrollment:
    """
    Elimina una inscripción (darse de baja).
    Recibe el objeto Enrollment (obtenido previamente) y lo elimina.
    """
    db.delete(db_enrollment)
    db.commit()
    return db_enrollment