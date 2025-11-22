# backend/app/crud/crud_student_profile.py
from sqlalchemy.orm import Session
from typing import Optional
from app.models.student_profile import StudentProfile
from app.schemas.student_profile import StudentProfileCreate, StudentProfileUpdate


def get_student_profile(db: Session, student_id: int) -> Optional[StudentProfile]:
    """Obtiene el perfil de un estudiante"""
    return db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()


def create_student_profile(
    db: Session, 
    student_id: int, 
    profile_in: StudentProfileCreate
) -> StudentProfile:
    """Crea un perfil de estudiante"""
    # Verificar si ya existe
    existing = get_student_profile(db, student_id)
    if existing:
        raise ValueError(f"El estudiante {student_id} ya tiene un perfil")
    
    db_profile = StudentProfile(
        student_id=student_id,
        motivation=profile_in.motivation,
        available_time=profile_in.available_time,
        sleep_hours=profile_in.sleep_hours,
        study_hours=profile_in.study_hours,
        enjoyment_studying=profile_in.enjoyment_studying,
        study_place_tranquility=profile_in.study_place_tranquility,
        academic_pressure=profile_in.academic_pressure,
        gender=profile_in.gender
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_student_profile(
    db: Session,
    student_id: int,
    profile_in: StudentProfileUpdate
) -> Optional[StudentProfile]:
    """Actualiza el perfil de un estudiante"""
    db_profile = get_student_profile(db, student_id)
    if not db_profile:
        return None
    
    # Actualizar solo los campos proporcionados
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


def get_or_create_student_profile(
    db: Session,
    student_id: int,
    profile_in: StudentProfileCreate
) -> StudentProfile:
    """Obtiene el perfil si existe, o lo crea si no existe"""
    existing = get_student_profile(db, student_id)
    if existing:
        return existing
    return create_student_profile(db, student_id, profile_in)

