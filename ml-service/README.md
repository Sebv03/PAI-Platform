# Microservicio de Machine Learning - PAI Platform

Microservicio independiente para la predicción de riesgo académico de estudiantes.

## Características

- **Predicción de Riesgo Académico**: Clasifica estudiantes en riesgo alto o bajo
- **Feature Engineering**: Calcula automáticamente 4 features clave:
  - Tasa de retraso en entregas
  - Tasa de no entrega
  - Promedio de notas
  - Variabilidad de notas
- **Modelo Random Forest**: Algoritmo de clasificación binaria
- **API REST**: Endpoints para entrenar y predecir

## Instalación

1. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

Editar `ml-service/core/config.py` para ajustar:
- `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL
- `MODEL_PATH`: Ruta donde se guardará el modelo entrenado
- `CORS_ORIGINS`: Orígenes permitidos para CORS

## Uso

### Iniciar el servidor

```bash
python main.py
```

O con uvicorn directamente:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

El servicio estará disponible en: `http://localhost:8001`

### Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Entrenar Modelo
```bash
POST /train
```

Entrena el modelo con los datos históricos de la base de datos.

**Respuesta:**
```json
{
  "status": "success",
  "accuracy": 0.85,
  "precision": 0.83,
  "recall": 0.85,
  "f1_score": 0.84,
  "samples_trained": 245,
  "message": "Modelo entrenado exitosamente con 245 muestras"
}
```

#### 3. Predecir Riesgo (Estudiante Individual)
```bash
POST /predict
Content-Type: application/json

{
  "student_id": 1,
  "course_id": 1
}
```

**Respuesta:**
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

#### 4. Predecir Riesgo (Todos los Estudiantes de un Curso)
```bash
GET /predict/batch?course_id=1
```

**Respuesta:**
```json
[
  {
    "student_id": 1,
    "course_id": 1,
    "risk_level": "alto",
    "risk_score": 0.75,
    "features": {...},
    "confidence": 0.65
  },
  {
    "student_id": 2,
    "course_id": 1,
    "risk_level": "bajo",
    "risk_score": 0.25,
    "features": {...},
    "confidence": 0.70
  }
]
```

## Features Calculadas

1. **submission_delay_rate** (0-1): 
   - Proporción de entregas que fueron tardías
   - 0 = todas a tiempo, 1 = todas tardías

2. **non_submission_rate** (0-1):
   - Proporción de tareas no entregadas
   - 0 = todas entregadas, 1 = ninguna entregada

3. **average_grade** (0-1):
   - Promedio de notas normalizado (escala original: 1.0-7.0)
   - 0 = promedio 1.0, 1 = promedio 7.0

4. **grade_variability** (0-1):
   - Variabilidad de notas (desviación estándar normalizada)
   - 0 = notas muy consistentes, 1 = notas muy variables

## Variable Objetivo (Y)

El modelo predice riesgo académico (alto/bajo) basado en:
- Promedio de notas < 4.0 (en escala 1-7), O
- Tasa de no entrega > 50%

## Integración con Backend Principal

El backend principal puede llamar a este microservicio para:
1. Obtener predicciones de riesgo para estudiantes
2. Mostrar alertas en el dashboard de docentes
3. Generar reportes de estudiantes en riesgo

**Ejemplo de integración desde el backend:**
```python
import httpx

async def get_student_risk(student_id: int, course_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/predict",
            json={"student_id": student_id, "course_id": course_id}
        )
        return response.json()
```

## Documentación de API

Una vez que el servidor esté corriendo, visita:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Notas

- El modelo se guarda automáticamente después del entrenamiento
- El modelo se carga automáticamente al iniciar el servicio si existe
- Se recomienda re-entrenar el modelo periódicamente con nuevos datos

