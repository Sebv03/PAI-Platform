# backend/app/api/endpoints/courses.py
from fastapi import APIRouter, Depends, HTTPException, status # <-- AÑADIR HTTPException y status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.course import Course, CourseCreate
# --- AÑADIR IMPORTACIONES DE TASK ---
from app.schemas.task import Task, TaskCreate
from app.crud import crud_course, crud_task # <-- AÑADIR crud_task
# ------------------------------------
from app.api import deps
from app.models.user import User, UserRole # <-- AÑADIR UserRole

router = APIRouter()

@router.get("/", response_model=List[Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Obtiene una lista de cursos creados por el usuario actual.
    """
    # --- CAMBIO AQUÍ: Pasamos el ID del usuario actual ---
    courses = crud_course.get_courses(db, owner_id=current_user.id, skip=skip, limit=limit)
    return courses

@router.post("/", response_model=Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: CourseCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crea un nuevo curso para el usuario actual.
    (Requiere rol de DOCENTE o ADMIN)
    """
    # Añadimos una comprobación de rol
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden crear cursos.",
        )
    
    course = crud_course.create_user_course(
        db, course_in=course_in, owner=current_user
    )
    return course


# --- AÑADIR ESTE NUEVO ENDPOINT ---

@router.post("/{course_id}/tasks/", response_model=Task)
def create_task_for_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crea una nueva tarea dentro de un curso específico.
    (Solo para el docente propietario del curso).
    """
    # 1. Verificar que el curso exista
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El curso no existe.",
        )
    
    # 2. Verificar que el usuario actual sea el dueño del curso
    if course.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para añadir tareas a este curso.",
        )
        
    # 3. Crear la tarea
    task = crud_task.create_course_task(db, task_in=task_in, course_id=course_id)
    return task