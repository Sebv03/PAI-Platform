# backend/app/api/endpoints/enrollments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.enrollment import Enrollment, EnrollmentCreate
from app.crud import crud_enrollment, crud_user, crud_course
from app.api import deps
from app.models.user import User, UserRole # Importamos el modelo y el Enum

router = APIRouter()

@router.post("/", response_model=Enrollment)
def create_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_in: EnrollmentCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crea una nueva matrícula (solo para docentes).
    """

    # --- REGLA 1: Solo docentes o admins pueden matricular ---
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción.",
        )

    # --- REGLA 2: El curso debe existir ---
    course = crud_course.get_course_by_id(
        db, course_id=enrollment_in.course_id
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El curso especificado no existe.",
        )
    
    

    # --- REGLA 3: El docente debe ser dueño del curso ---
    if course.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes matricular alumnos en un curso que no te pertenece.",
        )

    # --- REGLA 4: El estudiante debe existir ---
    student = crud_user.get_user_by_id(
        db, user_id=enrollment_in.student_id
    )
    if not student or student.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ID de estudiante proporcionado no existe o no es un estudiante.",
        )

    # --- REGLA 5: No se puede duplicar la matrícula ---
    existing_enrollment = crud_enrollment.get_by_student_and_course(
        db,
        student_id=enrollment_in.student_id,
        course_id=enrollment_in.course_id,
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este estudiante ya está matriculado en este curso.",
        )

    # --- Si todo pasa, se crea la matrícula ---
    enrollment = crud_enrollment.create_enrollment(
        db, enrollment_in=enrollment_in
    )
    return enrollment