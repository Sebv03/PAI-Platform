# backend/app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, File, UploadFile, Form # <-- Añade File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional
from datetime import datetime # Para validación de fechas
import os
import shutil
from pathlib import Path

from app.api import deps
from app.crud import crud_task, crud_course # Necesitamos crud_course para verificar si el curso existe
from app.schemas.task import Task, TaskCreate, TaskUpdate # Importamos los esquemas de Task
from app.models.user import User as UserModel # Importamos el modelo User para tipos de current_user
from app.models.user import UserRole # Para verificar roles
from app.schemas.submission import Submission, SubmissionCreate
from app.crud import crud_submission, crud_enrollment

router = APIRouter()

# ----------------- Endpoint para crear una nueva tarea -----------------
@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Crea una nueva tarea. Solo docentes pueden crear tareas.
    La tarea debe estar asociada a un curso existente que sea propiedad del docente.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes o administradores pueden crear tareas."
        )
    
    # Verificar que el curso existe y pertenece al usuario actual (docente)
    course = crud_course.get_course_by_id(db, course_id=task_in.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso con ID {task_in.course_id} no existe."
        )
    if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear tareas en este curso."
        )

    # La fecha de entrega no puede ser en el pasado (opcional, pero buena práctica)
    if task_in.due_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de entrega no puede ser en el pasado."
        )

    task = crud_task.create_task(db, task_in=task_in, course_id=task_in.course_id)
    return task

# ----------------- Endpoint para obtener una tarea por ID -----------------
@router.get("/{task_id}", response_model=Task)
async def read_task_by_id(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene una tarea por su ID.
    Acceso: Docente del curso, estudiante inscrito en el curso, o administrador.
    """
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada."
        )

    course = crud_course.get_course_by_id(db, course_id=task.course_id)
    if not course: # Esto no debería pasar si la FK es correcta, pero es un buen check
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso asociado a la tarea no encontrado."
        )

    # Lógica de Permisos Unificada
    if current_user.role == UserRole.ADMINISTRADOR:
        return task

    if current_user.id == course.owner_id: # Docente propietario del curso
        return task

    if current_user.role == UserRole.ESTUDIANTE:
        # Verificar si el estudiante está inscrito en el curso
        enrollment = crud_enrollment.get_enrollment_by_user_and_course(
            db, student_id=current_user.id, course_id=course.id
        )
        if enrollment: # Si hay una inscripción, el estudiante puede ver la tarea
            return task

    # Si ninguna de las condiciones anteriores se cumple, denegar el acceso
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para ver esta tarea."
    )

# ----------------- Endpoint para obtener tareas de un curso -----------------
@router.get("/course/{course_id}", response_model=List[Task])
async def read_tasks_by_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Obtiene todas las tareas para un curso específico.
    Acceso: Docente del curso, estudiante inscrito en el curso, o administrador.
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso con ID {course_id} no existe."
        )

    # Lógica de Permisos Unificada
    if current_user.role == UserRole.ADMINISTRADOR:
        tasks = crud_task.get_tasks_by_course(db, course_id=course_id, skip=skip, limit=limit)
        return tasks

    if current_user.id == course.owner_id: # Docente propietario
        tasks = crud_task.get_tasks_by_course(db, course_id=course_id, skip=skip, limit=limit)
        return tasks

    if current_user.role == UserRole.ESTUDIANTE:
        # Verificar si el estudiante está inscrito en el curso
        enrollment = crud_enrollment.get_enrollment_by_user_and_course(
            db, student_id=current_user.id, course_id=course_id
        )
        if enrollment: # Si hay una inscripción, el estudiante puede ver las tareas
            tasks = crud_task.get_tasks_by_course(db, course_id=course_id, skip=skip, limit=limit)
            return tasks

    # Si ninguna de las condiciones anteriores se cumple, denegar el acceso
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para ver las tareas de este curso."
    )

# ----------------- Endpoint para actualizar una tarea -----------------
@router.put("/{task_id}", response_model=Task)
async def update_existing_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Actualiza una tarea existente. Solo docentes o administradores pueden actualizar tareas.
    El docente debe ser el propietario del curso al que pertenece la tarea.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes o administradores pueden actualizar tareas."
        )

    db_task = crud_task.get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada."
        )
    
    # Verificar que el usuario actual es el propietario del curso de la tarea
    course = crud_course.get_course_by_id(db, course_id=db_task.course_id)
    if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta tarea."
        )

    # La fecha de entrega no puede ser en el pasado si se actualiza a una fecha pasada
    if task_in.due_date and task_in.due_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de entrega no puede ser en el pasado."
        )

    task = crud_task.update_task(db, db_task=db_task, task_in=task_in)
    return task

# ----------------- Endpoint para eliminar una tarea -----------------
# ¡REINTRODUCIMOS ESTA RUTA CON LA CORRECCIÓN!
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Response: # <-- Cambiado a Response para que no devuelva cuerpo
    """
    Elimina una tarea existente. Solo docentes o administradores pueden eliminar tareas.
    El docente debe ser el propietario del curso al que pertenece la tarea.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes o administradores pueden eliminar tareas."
        )

    db_task = crud_task.get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada."
        )
    
    course = crud_course.get_course_by_id(db, course_id=db_task.course_id)
    if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta tarea."
        )

    crud_task.delete_task(db, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT) # <-- ¡La corrección clave!


@router.post("/{task_id}/submit", response_model=Submission, status_code=status.HTTP_201_CREATED)
async def submit_task(
    task_id: int,
    file: UploadFile = File(None),
    content: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Permite a un estudiante autenticado entregar una tarea.
    """
    # 1. Verificar que el usuario es un estudiante
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden entregar tareas."
        )

    # 2. Verificar que la tarea existe
    task = crud_task.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La tarea no existe."
        )

    # 3. ¡NUEVO! Verificar que el estudiante esté inscrito en el curso de la tarea
    enrollment = crud_enrollment.get_enrollment_by_user_and_course(
        db, student_id=current_user.id, course_id=task.course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás inscrito en el curso de esta tarea."
        )

    # 4. Verificar que el estudiante no haya entregado ya esta tarea
    existing_submission = crud_submission.get_submission_by_task_and_student(
        db, task_id=task_id, student_id=current_user.id
    )
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has entregado esta tarea. Puedes editar tu entrega existente."
        )

    # 5. Validar que se haya enviado contenido o archivo
    if not file and not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar un archivo PDF o un contenido de texto."
        )

    # 6. Manejar archivo PDF si se envió
    file_path = None
    if file:
        # Validar que sea un PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos PDF."
            )
        
        # Crear directorio de uploads si no existe
        from app.core.config import settings
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre único para el archivo
        file_extension = Path(file.filename).suffix
        file_name = f"task_{task_id}_student_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        file_path = str(upload_dir / file_name)
        
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # 7. Crear la entrega
    submission_in = SubmissionCreate(content=content, file_path=file_path)
    submission = crud_submission.create_submission(
        db, submission_in=submission_in, task_id=task_id, student_id=current_user.id, file_path=file_path
    )
    return submission