from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_enrollment, crud_course
from app.schemas.enrollment import Enrollment, EnrollmentCreate # Asegúrate que EnrollmentCreate esté en schemas/enrollment.py
from app.schemas.course import Course as CourseSchema # Usamos el schema de Course para la respuesta
from app.models.user import User as UserModel
from app.models.user import UserRole

router = APIRouter()

# ----------------- Endpoint para OBTENER los cursos inscritos del ESTUDIANTE actual -----------------
@router.get("/me", response_model=List[CourseSchema])
async def read_my_enrollments(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene la lista de cursos en los que el estudiante actual está inscrito.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(status_code=403, detail="Solo los estudiantes pueden ver sus inscripciones.")
        
    courses = crud_enrollment.get_enrolled_courses_by_student(db, student_id=current_user.id)
    return courses

# ----------------- Endpoint para INSCRIBIR al ESTUDIANTE actual en un curso -----------------
@router.post("/", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
async def enroll_student_in_course(
    enrollment_in: EnrollmentCreate, # Recibimos el course_id desde el schema
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Inscribe al usuario (estudiante) actual en un curso.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(status_code=403, detail="Solo los estudiantes pueden inscribirse en cursos.")

    course = crud_course.get_course_by_id(db, course_id=enrollment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # Verificar que el estudiante no sea el dueño del curso (un docente no se inscribe a su propio curso)
    if course.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes inscribirte en tu propio curso.")

    existing = crud_enrollment.get_enrollment_by_user_and_course(db, student_id=current_user.id, course_id=enrollment_in.course_id)
    if existing:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este curso.")
    
    enrollment = crud_enrollment.create_enrollment(db, student_id=current_user.id, course_id=enrollment_in.course_id)
    return enrollment