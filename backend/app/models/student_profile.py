# backend/app/models/student_profile.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class StudentProfile(Base):
    """
    Modelo para almacenar el cuestionario de perfil del estudiante.
    Estas variables se usan como features predictivas para el modelo ML.
    """
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Variables del cuestionario (escala 1-10)
    motivation = Column(Float, nullable=False, comment="Nivel de motivación (1-10)")
    available_time = Column(Float, nullable=False, comment="Tiempo disponible para estudiar (1-10)")
    sleep_hours = Column(Float, nullable=False, comment="Horas de sueño por noche (1-10)")
    study_hours = Column(Float, nullable=False, comment="Horas dedicadas a estudiar (1-10)")
    enjoyment_studying = Column(Float, nullable=False, comment="Qué tanto le gusta estudiar (1-10)")
    study_place_tranquility = Column(Float, nullable=False, comment="Tranquilidad del lugar de estudio (1-10)")
    academic_pressure = Column(Float, nullable=False, comment="Presión académica percibida (1-10)")
    
    # Variable categórica
    gender = Column(String(20), nullable=True, comment="Género del estudiante")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con User
    student = relationship("User", back_populates="student_profile")

