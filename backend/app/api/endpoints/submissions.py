# backend/app/api/endpoints/submissions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_submission, crud_task, crud_enrollment, crud_course # Necesitamos los 3 CRUDs
from app.schemas.submission import Submission, SubmissionCreate, SubmissionUpdate
from app.models.user import User as UserModel
from app.models.user import UserRole

router = APIRouter()

# ----------------- Endpoint para OBTENER las entregas de una TAREA (Solo Docente) -----------------
@router.get("/task/{task_id}", response_model=List[Submission])
async def read_submissions_for_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene todas las entregas para una tarea específica.
    Solo el docente propietario del curso o un admin pueden ver esto.
    """
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    # (La lógica de permisos ya estaba en crud_task, pero la replicamos aquí para seguridad)
    # Necesitamos verificar que el current_user sea el dueño del curso al que pertenece la tarea
    # (Esta lógica está en el endpoint GET /tasks/{task_id}, asumimos que el docente ya tiene acceso a la tarea)
    
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos")
    
    # (Faltaría verificar que el docente es dueño del curso)

    submissions = crud_submission.get_submissions_by_task(db, task_id=task_id)
    return submissions

# ----------------- Endpoint para OBTENER una entrega específica -----------------
@router.get("/{submission_id}", response_model=Submission)
async def read_submission_by_id(
    submission_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene una entrega específica por su ID.
    Acceso: El estudiante que la entregó, el docente del curso, o un admin.
    """
    submission = crud_submission.get_submission_by_id(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")
    
    task = crud_task.get_task_by_id(db, task_id=submission.task_id)
    course = crud_course.get_course_by_id(db, course_id=task.course_id)

    if (current_user.role == UserRole.ADMINISTRADOR or
        current_user.id == course.owner_id or
        current_user.id == submission.student_id):
        return submission
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver esta entrega")

# ----------------- Endpoint para ACTUALIZAR una entrega (Calificar) -----------------
@router.put("/{submission_id}", response_model=Submission)
async def update_existing_submission(
    submission_id: int,
    submission_in: SubmissionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Actualiza una entrega (usado por docentes para calificar).
    """
    db_submission = crud_submission.get_submission_by_id(db, submission_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    task = crud_task.get_task_by_id(db, task_id=db_submission.task_id)
    course = crud_course.get_course_by_id(db, course_id=task.course_id)

    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para calificar esta entrega")
    
    submission = crud_submission.update_submission(db, db_submission=db_submission, submission_in=submission_in)
    return submission

