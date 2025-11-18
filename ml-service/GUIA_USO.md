# Guía de Uso del Microservicio ML

## Paso 1: Verificar que el Servidor Esté Funcionando

El servidor debería estar corriendo en `http://localhost:8001`

Puedes verificar:
- Health check: http://localhost:8001/health
- Documentación Swagger: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Paso 2: Entrenar el Modelo

Si aún no has entrenado el modelo, ejecuta:

```bash
cd ml-service
python train_model.py
```

Esto:
- Obtendrá los datos históricos de la base de datos
- Calculará las features (tasa de retraso, no entrega, promedio, variabilidad)
- Entrenará el modelo Random Forest
- Guardará el modelo en `models/risk_prediction_model.pkl`
- Mostrará las métricas del modelo (accuracy, precision, recall, F1-score)

## Paso 3: Probar los Endpoints

### 3.1 Entrenar el Modelo (si no lo has hecho)
```bash
POST http://localhost:8001/train
```

O desde Python:
```python
import requests
response = requests.post("http://localhost:8001/train")
print(response.json())
```

### 3.2 Predecir Riesgo de un Estudiante
```bash
POST http://localhost:8001/predict
Content-Type: application/json

{
  "student_id": 1,
  "course_id": 1
}
```

O desde Python:
```python
import requests
response = requests.post(
    "http://localhost:8001/predict",
    json={"student_id": 1, "course_id": 1}
)
print(response.json())
```

**Respuesta esperada:**
```json
{
  "student_id": 1,
  "course_id": 1,
  "risk_level": "alto",
  "risk_score": 0.75,
  "features": {
    "submission_delay_rate": 0.4,
    "non_submission_rate": 0.3,
    "average_grade": 0.5,
    "grade_variability": 0.2
  },
  "confidence": 0.65
}
```

### 3.3 Predecir Riesgo de Todos los Estudiantes de un Curso
```bash
GET http://localhost:8001/predict/batch?course_id=1
```

O desde Python:
```python
import requests
response = requests.get(
    "http://localhost:8001/predict/batch",
    params={"course_id": 1}
)
print(response.json())
```

## Paso 4: Integrar con el Backend Principal (Opcional pero Recomendado)

### 4.1 Crear el servicio de integración

Crea `backend/app/services/ml_service.py`:

```python
import httpx
from typing import Optional, Dict, Any

ML_SERVICE_URL = "http://localhost:8001"

async def get_student_risk_prediction(
    student_id: int, 
    course_id: int
) -> Optional[Dict[str, Any]]:
    """Obtiene la predicción de riesgo para un estudiante"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/predict",
                json={"student_id": student_id, "course_id": course_id}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None

async def get_course_risk_predictions(course_id: int) -> Optional[list]:
    """Obtiene las predicciones de riesgo para todos los estudiantes de un curso"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ML_SERVICE_URL}/predict/batch",
                params={"course_id": course_id}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error al conectar con el servicio ML: {e}")
        return None
```

### 4.2 Crear endpoints en el backend

Crea `backend/app/api/endpoints/ml_predictions.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.services.ml_service import (
    get_student_risk_prediction, 
    get_course_risk_predictions
)

router = APIRouter()

@router.get("/student/{student_id}/course/{course_id}")
async def get_student_risk(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene la predicción de riesgo para un estudiante"""
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones"
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
    """Obtiene las predicciones de riesgo para todos los estudiantes de un curso"""
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=403,
            detail="Solo docentes y administradores pueden ver predicciones"
        )
    
    predictions = await get_course_risk_predictions(course_id)
    if predictions is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio de ML no está disponible"
        )
    return predictions
```

### 4.3 Registrar el router en main.py

En `backend/app/main.py`, agrega:

```python
from app.api.endpoints import ml_predictions

app.include_router(
    ml_predictions.router,
    prefix=f"{settings.API_V1_STR}/ml",
    tags=["ML Predictions"]
)
```

### 4.4 Agregar httpx a requirements.txt

En `backend/requirements.txt`, agrega:

```
httpx==0.27.0
```

## Paso 5: Usar desde el Frontend

### 5.1 Agregar función en api.js

En `frontend/src/services/api.js`, agrega:

```javascript
// Obtener predicción de riesgo para un estudiante
export const getStudentRisk = async (studentId, courseId) => {
  const response = await api.get(`/ml/student/${studentId}/course/${courseId}`);
  return response.data;
};

// Obtener predicciones de riesgo para todos los estudiantes de un curso
export const getCourseRisks = async (courseId) => {
  const response = await api.get(`/ml/course/${courseId}`);
  return response.data;
};
```

### 5.2 Crear componente de indicador de riesgo

Crea `frontend/src/components/RiskIndicator.jsx`:

```jsx
import { useState, useEffect } from 'react';
import { getStudentRisk } from '../services/api';

const RiskIndicator = ({ studentId, courseId }) => {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const data = await getStudentRisk(studentId, courseId);
        setRisk(data);
      } catch (error) {
        console.error('Error al obtener predicción de riesgo:', error);
      } finally {
        setLoading(false);
      }
    };

    if (studentId && courseId) {
      fetchRisk();
    }
  }, [studentId, courseId]);

  if (loading) return <span className="badge">Cargando...</span>;
  if (!risk) return null;

  const riskClass = risk.risk_level === 'alto' ? 'badge-danger' : 'badge-success';
  const riskText = risk.risk_level === 'alto' ? 'Riesgo Alto' : 'Riesgo Bajo';

  return (
    <div className={`badge ${riskClass}`} title={`Confianza: ${(risk.confidence * 100).toFixed(1)}%`}>
      {riskText}
    </div>
  );
};

export default RiskIndicator;
```

### 5.3 Usar en la tabla de estudiantes

En `frontend/src/components/EnrolledStudentsTable.jsx`, agrega:

```jsx
import RiskIndicator from './RiskIndicator';

// Dentro de la tabla, en la columna de acciones:
<td>
  <RiskIndicator studentId={student.id} courseId={courseId} />
</td>
```

## Resumen de Próximos Pasos

1. ✅ **Servidor ML corriendo** - Ya está hecho
2. ⏭️ **Entrenar modelo** - Ejecuta `python train_model.py`
3. ⏭️ **Probar endpoints** - Usa Swagger UI en http://localhost:8001/docs
4. ⏭️ **Integrar con backend** - Crea los archivos de integración
5. ⏭️ **Mostrar en frontend** - Agrega componentes de visualización

## Comandos Útiles

```bash
# Entrenar modelo
cd ml-service
python train_model.py

# Iniciar servidor ML
python main.py

# Ver logs del servidor
# (se muestran en la consola donde ejecutaste python main.py)

# Probar endpoint desde terminal (Windows PowerShell)
Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET
```

## Troubleshooting

- **Error: "El modelo no está entrenado"**: Ejecuta `python train_model.py`
- **Error: "No hay datos históricos"**: Ejecuta `python populate_historical_data.py` en el backend
- **Error de conexión**: Verifica que el servidor ML esté corriendo en el puerto 8001
- **Error de CORS**: Verifica que `CORS_ORIGINS` en `ml-service/core/config.py` incluya tu frontend

