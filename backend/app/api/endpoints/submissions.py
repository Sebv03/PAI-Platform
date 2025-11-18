# backend/app/api/endpoints/submissions.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Any
from pathlib import Path
import os

from app.api import deps
from app.crud import crud_submission, crud_task, crud_enrollment, crud_course # Necesitamos los 3 CRUDs
from app.schemas.submission import Submission, SubmissionCreate, SubmissionUpdate, SubmissionWithStudent
from app.models.user import User as UserModel
from app.models.user import UserRole

router = APIRouter()

# ----------------- Endpoint para OBTENER las entregas de una TAREA (Solo Docente) -----------------
@router.get("/task/{task_id}", response_model=List[SubmissionWithStudent])
async def read_submissions_for_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene todas las entregas para una tarea específica con información del estudiante.
    Solo el docente propietario del curso o un admin pueden ver esto.
    """
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    course = crud_course.get_course_by_id(db, course_id=task.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    # Verificar permisos: solo el docente propietario o admin
    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para ver las entregas de esta tarea"
        )

    # Obtener entregas con información del estudiante
    submissions = crud_submission.get_submissions_by_task(db, task_id=task_id)
    
    # Cargar información del estudiante para cada entrega y construir respuesta
    from app.crud import crud_user
    from app.schemas.submission import SubmissionWithStudent
    
    result = []
    for submission in submissions:
        student = crud_user.get_user_by_id(db, user_id=submission.student_id)
        
        # Convertir submission a dict y agregar información del estudiante
        submission_dict = {
            "id": submission.id,
            "content": submission.content,
            "file_path": submission.file_path,
            "submitted_at": submission.submitted_at,
            "student_id": submission.student_id,
            "task_id": submission.task_id,
            "grade": submission.grade,
            "feedback": submission.feedback,
            "student_name": None,
            "student_email": None
        }
        
        if student:
            submission_dict["student_name"] = getattr(student, 'full_name', None) or f"Usuario {student.id}"
            submission_dict["student_email"] = student.email
        
        result.append(SubmissionWithStudent(**submission_dict))
    
    return result

# ----------------- Endpoint para OBTENER la entrega del estudiante para una tarea específica -----------------
@router.get("/task/{task_id}/my-submission", response_model=Submission)
async def read_my_submission_for_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene la entrega del estudiante actual para una tarea específica.
    Solo estudiantes pueden acceder a este endpoint.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Solo estudiantes pueden ver sus entregas"
        )
    
    # Verificar que la tarea existe
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tarea no encontrada"
        )
    
    # Verificar que el estudiante esté inscrito en el curso
    enrollment = crud_enrollment.get_enrollment_by_user_and_course(
        db, student_id=current_user.id, course_id=task.course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás inscrito en el curso de esta tarea"
        )
    
    try:
        submission = crud_submission.get_submission_by_task_and_student(
            db, task_id=task_id, student_id=current_user.id
        )
    except Exception as e:
        print(f"DEBUG: Error al obtener entrega: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la entrega: {str(e)}"
        )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No has entregado esta tarea aún"
        )
    
    return submission

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
    Permite asignar una nota (1.0 a 7.0) y feedback.
    """
    db_submission = crud_submission.get_submission_by_id(db, submission_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    task = crud_task.get_task_by_id(db, task_id=db_submission.task_id)
    course = crud_course.get_course_by_id(db, course_id=task.course_id)

    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para calificar esta entrega"
        )
    
    # Validar que la nota esté en el rango válido (1.0 a 7.0)
    if submission_in.grade is not None:
        if submission_in.grade < 1.0 or submission_in.grade > 7.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La calificación debe estar entre 1.0 y 7.0"
            )
    
    submission = crud_submission.update_submission(db, db_submission=db_submission, submission_in=submission_in)
    return submission

# ----------------- Endpoint para DESCARGAR el PDF de una entrega -----------------
@router.get("/{submission_id}/download")
async def download_submission_file(
    submission_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Descarga el archivo PDF de una entrega.
    Acceso: El estudiante que la entregó, el docente del curso, o un admin.
    """
    submission = crud_submission.get_submission_by_id(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")
    
    if not submission.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esta entrega no tiene archivo adjunto")
    
    task = crud_task.get_task_by_id(db, task_id=submission.task_id)
    course = crud_course.get_course_by_id(db, course_id=task.course_id)

    # Verificar permisos
    if not (current_user.role == UserRole.ADMINISTRADOR or
            current_user.id == course.owner_id or
            current_user.id == submission.student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para descargar este archivo")
    
    # Verificar que el archivo existe
    file_path = Path(submission.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo no existe en el servidor")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/pdf'
    )

