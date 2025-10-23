# backend/app/crud/crud_task.py
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate

def create_course_task(
    db: Session, *, task_in: TaskCreate, course_id: int
) -> Task:
    """
    Crea una nueva tarea y la asocia a un curso.
    """
    # Convertimos el schema Pydantic a un diccionario
    task_data = task_in.model_dump()

    # Creamos la instancia del modelo SQLAlchemy, añadiendo el course_id
    db_task = Task(**task_data, course_id=course_id)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

def get_task_by_id(db: Session, *, task_id: int) -> Task | None:
    """
    Busca una tarea por su ID.
    """
    return db.query(Task).filter(Task.id == task_id).first()