# backend/app/models/course.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime # <-- Asegúrate de tener DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # <-- Asegúrate de importar func
from app.db.base import Base
from sqlalchemy.sql import text

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # --- ¡ESTA LÍNEA ES CRÍTICA! ---
    created_at = Column(DateTime, server_default=text("NOW()"), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="course", cascade="all, delete-orphan")