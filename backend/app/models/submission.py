# backend/app/models/submission.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.sql import text

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False) # Contenido de la entrega (ej. texto, enlace a archivo)
    grade = Column(Integer, nullable=True) # Calificación, puede ser nulo al principio
    feedback = Column(String, nullable=True) # Comentarios del docente
    submission_date = Column(DateTime, server_default=text("NOW()"), nullable=False)

    # Foreign Keys
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # --- RELACIONES ---
    # Una entrega pertenece a un estudiante (User)
    student = relationship("User", back_populates="submissions") # <--- USA CADENA

    # Una entrega pertenece a una tarea (Task)
    task = relationship("Task", back_populates="submissions") # <--- USA CADENA

    def __repr__(self):
        return f"<Submission(id={self.id}, student_id={self.student_id}, task_id={self.task_id})>"