# backend/app/models/submission.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False) # Contenido de la entrega o URL a un archivo
    submitted_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id")) # Asumiendo que las entregas son para tareas

    # --- RELACIONES DE VUELTA ---
    user = relationship("User", back_populates="submissions") # <--- Esta es la clave
    task = relationship("Task", back_populates="submissions") # Si las tareas tienen submissions