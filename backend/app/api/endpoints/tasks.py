# backend/app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_task, crud_course # Necesitamos crud_course para verificar si el curso existe
from app.schemas.task import Task, TaskCreate, TaskUpdate # Importamos los esquemas de Task
from app.models.user import User as UserModel # Importamos el modelo User para tipos de current_user
from app.models.user import UserRole # Para verificar roles

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

    task = crud_task.create_task(db, task_in=task_in)
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
    
    # Verificar permisos (docente del curso, estudiante inscrito, administrador)
    course = crud_course.get_course_by_id(db, course_id=task.course_id)
    
    if current_user.role == UserRole.ADMINISTRADOR:
        return task
    
    if current_user.id == course.owner_id: # Docente propietario del curso
        return task
    
    # Verificar si el usuario es un estudiante inscrito en el curso
    # Esto requeriría crud_enrollment.is_user_enrolled(db, user_id=current_user.id, course_id=course.id)
    # Por ahora, si no es admin ni docente, se deniega. Lo implementaremos más adelante.
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
    
    if current_user.role == UserRole.ADMINISTRADOR:
        tasks = crud_task.get_tasks_by_course(db, course_id=course_id, skip=skip, limit=limit)
        return tasks
    
    if current_user.id == course.owner_id: # Docente propietario
        tasks = crud_task.get_tasks_by_course(db, course_id=course_id, skip=skip, limit=limit)
        return tasks
    
    # Aquí iría la verificación para estudiantes inscritos (requiere crud_enrollment)
    # Por ahora, si no es admin ni docente, se deniega.
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

    task = crud_task.update_task(db, db_task=db_task, task_in=task_in)
    return task

# ----------------- Endpoint para eliminar una tarea -----------------
##@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
#async def delete_existing_task(
 #   task_id: int,
  #  db: Session = Depends(deps.get_db),
  #  current_user: UserModel = Depends(deps.get_current_user)
#) -> Any:
    """
    Elimina una tarea existente. Solo docentes o administradores pueden eliminar tareas.
    El docente debe ser el propietario del curso al que pertenece la tarea.
    """
  #  if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
     #   raise HTTPException(
      #      status_code=status.HTTP_403_FORBIDDEN,
       #     detail="Solo docentes o administradores pueden eliminar tareas."
     #   )

   # db_task = crud_task.get_task_by_id(db, task_id=task_id)
   # if not db_task:
      #  raise HTTPException(
     #       status_code=status.HTTP_404_NOT_FOUND,
    #        detail="Tarea no encontrada."
   #     )
    
  #  # Verificar que el usuario actual es el propietario del curso de la tarea
 #   course = crud_course.get_course_by_id(db, course_id=db_task.course_id)
  #  if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
 #       raise HTTPException(
  #          status_code=status.HTTP_403_FORBIDDEN,
 #           detail="No tienes permiso para eliminar esta tarea."
  #      )

  #  crud_task.delete_task(db, task_id=task_id)
  #  # ¡CORRECCIÓN AQUÍ! No devolver nada para 204 No Content
  #  return Response(status_code=status.HTTP_204_NO_CONTENT)##