# backend/app/models/task.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship # <-- SÍ IMPORTA relationship
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.sql import text
# from typing import List # No es estrictamente necesario aquí si no tipas la relación

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    due_date = Column(DateTime, nullable=False) # func.now sin paréntesis
    created_at = Column(DateTime, server_default=text("NOW()"), nullable=False) 

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # --- Relaciones ---
    course = relationship("Course", back_populates="tasks") # <--- USA CADENA
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan") # <--- USA CADENA

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', course_id={self.course_id})>"