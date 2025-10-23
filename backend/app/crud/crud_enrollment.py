# backend/app/crud/crud_enrollment.py
from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate

def get_by_student_and_course(
    db: Session, *, student_id: int, course_id: int
) -> Enrollment | None:
    """
    Verifica si ya existe una matrícula para este estudiante en este curso.
    """
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
        .first()
    )

def create_enrollment(
    db: Session, *, enrollment_in: EnrollmentCreate
) -> Enrollment:
    """
    Crea una nueva matrícula.
    """
    db_enrollment = Enrollment(
        student_id=enrollment_in.student_id,
        course_id=enrollment_in.course_id,
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def get_by_student_and_course(
    db: Session, *, student_id: int, course_id: int
) -> Enrollment | None:
    """
    Verifica si un estudiante está matriculado en un curso.
    """
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
        .first()
    )