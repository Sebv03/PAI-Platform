# backend/app/models/course.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship # <-- Asegúrate de importar relationship

from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id")) # La clave foránea apunta a users.id

    # --- ASEGÚRATE DE QUE ESTAS RELACIONES ESTÉN PRESENTES Y CORRECTAS ---
    # Un curso tiene un solo propietario (owner)
    owner = relationship("User", back_populates="courses") # <--- Y ESTO ES CRÍTICO
    # Un curso puede tener muchas tareas
    tasks = relationship("Task", back_populates="course")
    # Un curso puede tener muchas inscripciones
    enrollments = relationship("Enrollment", back_populates="course")