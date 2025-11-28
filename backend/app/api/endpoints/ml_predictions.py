"""
Endpoints para obtener predicciones de riesgo académico del servicio ML
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.services.ml_service import (
    get_student_risk_prediction, 
    get_course_risk_predictions,
    train_ml_model,
    get_student_profile_prediction
)

router = APIRouter()


@router.get("/student/{student_id}/course/{course_id}")
async def get_student_risk(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene la predicción de riesgo académico para un estudiante en un curso específico.
    Solo docentes y administradores pueden ver estas predicciones.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones de riesgo"
        )
    
    prediction = await get_student_risk_prediction(student_id, course_id)
    
    if prediction is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible. Verifica que esté corriendo en http://localhost:8001"
        )
    
    return prediction


@router.get("/course/{course_id}")
async def get_course_risks(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene las predicciones de riesgo académico para todos los estudiantes de un curso.
    Solo docentes y administradores pueden ver estas predicciones.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones de riesgo"
        )
    
    predictions = await get_course_risk_predictions(course_id)
    
    if predictions is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible. Verifica que esté corriendo en http://localhost:8001"
        )
    
    return predictions


@router.get("/student/{student_id}/profile-prediction")
async def get_student_profile_risk(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene la predicción de riesgo académico para un estudiante basándose SOLO en su perfil del cuestionario.
    Esta predicción puede hacerse antes de que el estudiante tenga datos transaccionales.
    Solo administradores y docentes pueden ver estas predicciones.
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones de riesgo"
        )
    
    prediction = await get_student_profile_prediction(student_id)
    
    if prediction is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible. Verifica que esté corriendo en http://localhost:8001"
        )
    
    return prediction


@router.post("/train")
async def train_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Entrena el modelo de ML con los datos históricos.
    Solo administradores pueden entrenar el modelo.
    """
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden entrenar el modelo"
        )
    
    result = await train_ml_model()
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible. Verifica que esté corriendo en http://localhost:8001"
        )
    
    return result

