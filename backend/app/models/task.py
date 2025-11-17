# backend/app/models/task.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text # Para el valor por defecto NOW()

from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Campo crítico para ML: Fecha límite de entrega
    due_date = Column(DateTime(timezone=True), nullable=False)
    
    # Campo de auditoría: Cuándo se creó la tarea
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    # Clave foránea al curso al que pertenece
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # --- Relaciones de SQLAlchemy ---

    # Relación de vuelta al Curso (Un curso tiene muchas tareas)
    course = relationship("Course", back_populates="tasks")
    
    # Relación con las Entregas (Una tarea tendrá muchas entregas)
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}')>"