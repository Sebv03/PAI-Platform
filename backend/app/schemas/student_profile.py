# backend/app/schemas/student_profile.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class StudentProfileBase(BaseModel):
    """Schema base para el perfil del estudiante"""
    motivation: float = Field(..., ge=1, le=10, description="Nivel de motivación (1-10)")
    available_time: float = Field(..., ge=1, le=10, description="Tiempo disponible para estudiar (1-10)")
    sleep_hours: float = Field(..., ge=1, le=10, description="Horas de sueño por noche (1-10)")
    study_hours: float = Field(..., ge=1, le=10, description="Horas dedicadas a estudiar (1-10)")
    enjoyment_studying: float = Field(..., ge=1, le=10, description="Qué tanto le gusta estudiar (1-10)")
    study_place_tranquility: float = Field(..., ge=1, le=10, description="Tranquilidad del lugar de estudio (1-10)")
    academic_pressure: float = Field(..., ge=1, le=10, description="Presión académica percibida (1-10)")
    gender: Optional[str] = Field(None, max_length=20, description="Género del estudiante")
    
    @validator('motivation', 'available_time', 'sleep_hours', 'study_hours', 
               'enjoyment_studying', 'study_place_tranquility', 'academic_pressure')
    def validate_scale(cls, v):
        """Valida que el valor esté en la escala 1-10"""
        if not 1 <= v <= 10:
            raise ValueError("El valor debe estar entre 1 y 10")
        return round(v, 1)  # Redondear a 1 decimal


class StudentProfileCreate(StudentProfileBase):
    """Schema para crear un perfil de estudiante"""
    pass


class StudentProfileUpdate(BaseModel):
    """Schema para actualizar un perfil de estudiante (todos los campos opcionales)"""
    motivation: Optional[float] = Field(None, ge=1, le=10)
    available_time: Optional[float] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=1, le=10)
    study_hours: Optional[float] = Field(None, ge=1, le=10)
    enjoyment_studying: Optional[float] = Field(None, ge=1, le=10)
    study_place_tranquility: Optional[float] = Field(None, ge=1, le=10)
    academic_pressure: Optional[float] = Field(None, ge=1, le=10)
    gender: Optional[str] = Field(None, max_length=20)
    
    @validator('motivation', 'available_time', 'sleep_hours', 'study_hours', 
               'enjoyment_studying', 'study_place_tranquility', 'academic_pressure', pre=True)
    def validate_scale(cls, v):
        """Valida que el valor esté en la escala 1-10"""
        if v is not None:
            if not 1 <= float(v) <= 10:
                raise ValueError("El valor debe estar entre 1 y 10")
            return round(float(v), 1)
        return v


class StudentProfile(StudentProfileBase):
    """Schema para leer un perfil de estudiante"""
    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

