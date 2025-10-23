# backend/app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.submission import Submission, SubmissionCreate
from app.crud import crud_submission, crud_task, crud_enrollment
from app.api import deps
from app.models.user import User, UserRole

router = APIRouter()

@router.post("/{task_id}/submit/", response_model=Submission)
def create_submission(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    submission_in: SubmissionCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Crea una nueva entrega para una tarea (solo para estudiantes matriculados).
    """

    # --- REGLA 1: Solo estudiantes pueden entregar tareas ---
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden entregar tareas.",
        )

    # --- REGLA 2: La tarea debe existir ---
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La tarea no existe.",
        )

    # --- REGLA 3: El estudiante debe estar matriculado en el curso ---
    enrollment = crud_enrollment.get_by_student_and_course(
        db, student_id=current_user.id, course_id=task.course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás matriculado en el curso al que pertenece esta tarea.",
        )

    # --- REGLA 4: No se puede entregar dos veces ---
    existing_submission = crud_submission.get_submission_by_student_and_task(
        db, student_id=current_user.id, task_id=task_id
    )
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has entregado esta tarea.",
        )

    # --- Si todo pasa, se crea la entrega ---
    submission = crud_submission.create_submission(
        db, submission_in=submission_in, task_id=task_id, student=current_user
    )
    return submission