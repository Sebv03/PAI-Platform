# Guía de Integración del Microservicio ML

Este documento explica cómo integrar el microservicio de ML con el backend principal.

## Configuración

1. Asegúrate de que el microservicio ML esté corriendo en `http://localhost:8001`
2. El backend principal debe poder hacer peticiones HTTP al microservicio

## Ejemplo de Integración

### 1. Agregar cliente HTTP al backend

En `backend/app/services/ml_service.py`:

```python
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

ML_SERVICE_URL = "http://localhost:8001"

async def get_student_risk_prediction(
    student_id: int, 
    course_id: int
) -> Optional[Dict[str, Any]]:
    """
    Obtiene la predicción de riesgo para un estudiante en un curso
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/predict",
                json={
                    "student_id": student_id,
                    "course_id": course_id
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP del servicio ML: {e}")
        return None


async def get_course_risk_predictions(
    course_id: int
) -> Optional[list]:
    """
    Obtiene las predicciones de riesgo para todos los estudiantes de un curso
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


async def train_ml_model() -> Optional[Dict[str, Any]]:
    """
    Entrena el modelo de ML con los datos históricos
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
```

### 2. Crear endpoint en el backend para obtener predicciones

En `backend/app/api/endpoints/ml_predictions.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ml_service import get_student_risk_prediction, get_course_risk_predictions

router = APIRouter()


@router.get("/student/{student_id}/course/{course_id}")
async def get_student_risk(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la predicción de riesgo para un estudiante en un curso
    Solo docentes y administradores pueden ver estas predicciones
    """
    from app.models.user import UserRole
    
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones de riesgo"
        )
    
    prediction = await get_student_risk_prediction(student_id, course_id)
    
    if prediction is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible"
        )
    
    return prediction


@router.get("/course/{course_id}")
async def get_course_risks(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las predicciones de riesgo para todos los estudiantes de un curso
    Solo docentes y administradores pueden ver estas predicciones
    """
    from app.models.user import UserRole
    
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones de riesgo"
        )
    
    predictions = await get_course_risk_predictions(course_id)
    
    if predictions is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible"
        )
    
    return predictions
```

### 3. Registrar el router en main.py

```python
from app.api.endpoints import ml_predictions

app.include_router(
    ml_predictions.router,
    prefix=f"{settings.API_V1_STR}/ml",
    tags=["ML Predictions"]
)
```

### 4. Agregar httpx a requirements.txt

```txt
httpx==0.27.0
```

## Uso desde el Frontend

El frontend puede llamar a estos endpoints del backend principal:

```javascript
// Obtener predicción de riesgo para un estudiante
const getStudentRisk = async (studentId, courseId) => {
  const response = await api.get(`/ml/student/${studentId}/course/${courseId}`);
  return response.data;
};

// Obtener predicciones de riesgo para todos los estudiantes de un curso
const getCourseRisks = async (courseId) => {
  const response = await api.get(`/ml/course/${courseId}`);
  return response.data;
};
```

## Ejemplo de Componente React

```jsx
import { useState, useEffect } from 'react';
import api from '../services/api';

const StudentRiskIndicator = ({ studentId, courseId }) => {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const data = await api.get(`/ml/student/${studentId}/course/${courseId}`);
        setRisk(data);
      } catch (error) {
        console.error('Error al obtener predicción de riesgo:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRisk();
  }, [studentId, courseId]);

  if (loading) return <div>Cargando...</div>;
  if (!risk) return null;

  return (
    <div className={`risk-indicator risk-${risk.risk_level}`}>
      <span>Riesgo: {risk.risk_level.toUpperCase()}</span>
      <span>Confianza: {(risk.confidence * 100).toFixed(1)}%</span>
    </div>
  );
};
```

## Notas Importantes

1. **Timeout**: El entrenamiento del modelo puede tardar varios minutos, asegúrate de configurar timeouts apropiados
2. **Error Handling**: Siempre maneja los casos en que el servicio ML no esté disponible
3. **Caché**: Considera implementar caché para las predicciones si no cambian frecuentemente
4. **Re-entrenamiento**: Programa re-entrenamientos periódicos del modelo (ej: semanalmente)

