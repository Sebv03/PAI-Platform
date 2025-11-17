# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Enum # <-- Importa Boolean y Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    PSICOPEDAGOGO = "psicopedagogo"
    ADMINISTRADOR = "administrador"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ESTUDIANTE, nullable=False)
    
    is_active = Column(Boolean, default=True) # <-- ¡AÑADE ESTA LÍNEA!

    # --- Relaciones ---
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"