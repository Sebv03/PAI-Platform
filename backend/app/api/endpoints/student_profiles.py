# backend/app/api/endpoints/student_profiles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.models.user import User, UserRole
from app.crud import crud_student_profile
from app.schemas.student_profile import (
    StudentProfile,
    StudentProfileCreate,
    StudentProfileUpdate
)

router = APIRouter()


@router.post("/", response_model=StudentProfile, status_code=status.HTTP_201_CREATED)
async def create_student_profile(
    profile_in: StudentProfileCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Crea o actualiza el perfil del estudiante actual.
    Solo estudiantes pueden crear/actualizar su propio perfil.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden completar el cuestionario de perfil."
        )
    
    try:
        # Intentar crear, si ya existe, actualizar
        existing = crud_student_profile.get_student_profile(db, current_user.id)
        if existing:
            # Actualizar perfil existente
            profile = crud_student_profile.update_student_profile(
                db, current_user.id, 
                StudentProfileUpdate(**profile_in.dict())
            )
        else:
            # Crear nuevo perfil
            profile = crud_student_profile.create_student_profile(
                db, current_user.id, profile_in
            )
        return profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=StudentProfile)
async def get_my_student_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene el perfil del estudiante actual.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden ver su perfil."
        )
    
    profile = crud_student_profile.get_student_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha completado el cuestionario de perfil."
        )
    
    return profile


@router.get("/student/{student_id}", response_model=StudentProfile)
async def get_student_profile_by_id(
    student_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene el perfil de un estudiante específico.
    Solo administradores, docentes o el propio estudiante pueden ver el perfil.
    """
    # Verificar permisos
    if current_user.role not in [UserRole.ADMINISTRADOR, UserRole.DOCENTE]:
        if current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este perfil."
            )
    
    profile = crud_student_profile.get_student_profile(db, student_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante no ha completado el cuestionario de perfil."
        )
    
    return profile


@router.put("/me", response_model=StudentProfile)
async def update_my_student_profile(
    profile_in: StudentProfileUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Actualiza el perfil del estudiante actual.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden actualizar su perfil."
        )
    
    profile = crud_student_profile.update_student_profile(
        db, current_user.id, profile_in
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha completado el cuestionario de perfil. Usa POST para crearlo."
        )
    
    return profile

