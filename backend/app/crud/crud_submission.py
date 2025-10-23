# backend/app/crud/crud_submission.py
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import SubmissionCreate

def get_submission_by_student_and_task(
    db: Session, *, student_id: int, task_id: int
) -> Submission | None:
    """
    Verifica si un estudiante ya entregó esta tarea.
    """
    return (
        db.query(Submission)
        .filter(
            Submission.student_id == student_id,
            Submission.task_id == task_id
        )
        .first()
    )

def create_submission(
    db: Session, *, submission_in: SubmissionCreate, task_id: int, student: User
) -> Submission:
    """
    Crea una nueva entrega para un estudiante y una tarea.
    El timestamp lo pone la base de datos por defecto.
    """
    db_submission = Submission(
        content=submission_in.content,
        task_id=task_id,
        student=student # Asignamos el objeto de usuario estudiante
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission