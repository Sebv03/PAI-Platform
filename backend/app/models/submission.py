# backend/app/models/submission.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text # Para el valor por defecto NOW()

from app.db.base import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contenido de la entrega (puede ser un texto o un enlace a un archivo)
    content = Column(Text, nullable=True)
    
    # Ruta del archivo PDF subido (si se entrega un PDF)
    file_path = Column(String(500), nullable=True) 
    
    # Calificación (nota de 1.0 a 7.0)
    grade = Column(Float, nullable=True)
    
    # Feedback del docente
    feedback = Column(Text, nullable=True)
    
    # Fecha de entrega (manejada por la base de datos)
    submitted_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    # Claves foráneas
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # --- Relaciones de SQLAlchemy ---
    
    # Relación de vuelta al Estudiante (Un usuario tiene muchas entregas)
    student = relationship("User", back_populates="submissions")
    
    # Relación de vuelta a la Tarea (Una tarea tiene muchas entregas)
    task = relationship("Task", back_populates="submissions")

    def __repr__(self):
        return f"<Submission(id={self.id}, student_id={self.student_id}, task_id={self.task_id})>"