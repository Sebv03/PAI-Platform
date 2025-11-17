# backend/app/crud/crud_task.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.task import Task # Importa el modelo de SQLAlchemy
from app.schemas.task import TaskCreate, TaskUpdate # Importa los esquemas de Pydantic

# ----------------- Crear una nueva tarea -----------------
def create_task(db: Session, task_in: TaskCreate, course_id: int) -> Task:
    """
    Crea una nueva tarea para un curso específico.
    """
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        course_id=course_id # Asignamos el course_id pasado directamente
        # 'created_at' será generado automáticamente por el server_default
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ----------------- Obtener una tarea por ID -----------------
def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """
    Obtiene una tarea específica por su ID.
    """
    return db.query(Task).filter(Task.id == task_id).first()

# ----------------- Obtener tareas por Course ID -----------------
def get_tasks_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Obtiene todas las tareas de un curso específico.
    """
    return db.query(Task).filter(Task.course_id == course_id).offset(skip).limit(limit).all()

# ----------------- Obtener todas las tareas (para administradores, etc.) -----------------
def get_all_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Obtiene todas las tareas existentes en la base de datos.
    """
    return db.query(Task).offset(skip).limit(limit).all()

# ----------------- Actualizar una tarea -----------------
def update_task(db: Session, db_task: Task, task_in: TaskUpdate) -> Task:
    """
    Actualiza una tarea existente en la base de datos.
    """
    # Usamos model_dump para Pydantic v2. exclude_unset=True para actualizar solo los campos enviados.
    update_data = task_in.model_dump(exclude_unset=True) 

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ----------------- Eliminar una tarea -----------------
def delete_task(db: Session, task_id: int) -> Optional[Task]:
    """
    Elimina una tarea específica por su ID.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task