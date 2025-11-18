"""
Servicio para comunicarse con el microservicio de ML
"""

import httpx
from typing import Optional, Dict, Any, List


ML_SERVICE_URL = "http://localhost:8001"


async def get_student_risk_prediction(
    student_id: int, 
    course_id: int
) -> Optional[Dict[str, Any]]:
    """
    Obtiene la predicción de riesgo para un estudiante en un curso
    
    Args:
        student_id: ID del estudiante
        course_id: ID del curso
    
    Returns:
        Dict con la predicción o None si hay error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/predict",
                json={"student_id": student_id, "course_id": course_id}
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP del servicio ML: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al obtener predicción: {e}")
        return None


async def get_course_risk_predictions(
    course_id: int
) -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene las predicciones de riesgo para todos los estudiantes de un curso
    
    Args:
        course_id: ID del curso
    
    Returns:
        Lista de predicciones o None si hay error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ML_SERVICE_URL}/predict/batch",
                params={"course_id": course_id}
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP del servicio ML: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al obtener predicciones: {e}")
        return None


async def train_ml_model() -> Optional[Dict[str, Any]]:
    """
    Entrena el modelo de ML con los datos históricos
    
    Returns:
        Dict con las métricas del entrenamiento o None si hay error
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minutos timeout
            response = await client.post(f"{ML_SERVICE_URL}/train")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP del servicio ML: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al entrenar modelo: {e}")
        return None

