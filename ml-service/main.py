"""
Microservicio de Machine Learning para Predicción de Riesgo Académico
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path

# Agregar el directorio actual al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from services.feature_engineering import FeatureEngineering
from services.model_service import ModelService
from services.data_service import DataService
from core.config import settings

app = FastAPI(
    title="PAI ML Service",
    description="Microservicio de Machine Learning para predicción de riesgo académico",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
data_service = DataService()
feature_engineering = FeatureEngineering()
model_service = ModelService()


class PredictionRequest(BaseModel):
    student_id: int
    course_id: int


class PredictionResponse(BaseModel):
    student_id: int
    course_id: int
    risk_level: str  # "alto" o "bajo"
    risk_score: float  # Probabilidad de riesgo (0-1)
    features: dict
    confidence: float


class TrainingResponse(BaseModel):
    status: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    samples_trained: int
    message: str


@app.get("/")
async def root():
    return {
        "service": "PAI ML Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model_service.is_model_loaded()
    return {
        "status": "healthy",
        "model_loaded": model_loaded
    }


@app.post("/train", response_model=TrainingResponse)
async def train_model():
    """
    Entrena el modelo de ML con los datos históricos de la base de datos
    """
    try:
        # Obtener datos históricos
        print("Obteniendo datos históricos...")
        historical_data = data_service.get_historical_data()
        
        if historical_data.empty:
            raise HTTPException(
                status_code=400,
                detail="No hay datos históricos disponibles para entrenar el modelo"
            )
        
        print(f"Datos obtenidos: {len(historical_data)} registros")
        
        # Feature engineering
        print("Calculando features...")
        features_df = feature_engineering.calculate_features(historical_data)
        
        if features_df.empty:
            raise HTTPException(
                status_code=400,
                detail="No se pudieron calcular features. Verifica que haya entregas con calificaciones."
            )
        
        print(f"Features calculadas: {len(features_df)} registros")
        
        # Entrenar modelo
        print("Entrenando modelo...")
        metrics = model_service.train_model(features_df)
        
        # Guardar modelo
        model_service.save_model()
        
        return TrainingResponse(
            status="success",
            accuracy=metrics.get("accuracy"),
            precision=metrics.get("precision"),
            recall=metrics.get("recall"),
            f1_score=metrics.get("f1_score"),
            samples_trained=len(features_df),
            message=f"Modelo entrenado exitosamente con {len(features_df)} muestras"
        )
    
    except Exception as e:
        print(f"Error al entrenar modelo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al entrenar el modelo: {str(e)}"
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict_risk(request: PredictionRequest):
    """
    Predice el riesgo académico de un estudiante en un curso específico
    """
    try:
        # Verificar que el modelo esté cargado
        if not model_service.is_model_loaded():
            # Intentar cargar el modelo guardado
            if not model_service.load_model():
                raise HTTPException(
                    status_code=503,
                    detail="El modelo no está entrenado. Por favor, entrena el modelo primero con /train"
                )
        
        # Obtener datos del estudiante en el curso
        student_data = data_service.get_student_course_data(
            student_id=request.student_id,
            course_id=request.course_id
        )
        
        if student_data is None or student_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para el estudiante {request.student_id} en el curso {request.course_id}"
            )
        
        # Calcular features
        features_df = feature_engineering.calculate_features(student_data)
        
        if features_df.empty:
            # Si no hay suficientes datos, retornar riesgo bajo por defecto
            return PredictionResponse(
                student_id=request.student_id,
                course_id=request.course_id,
                risk_level="bajo",
                risk_score=0.3,
                features={},
                confidence=0.5
            )
        
        # Obtener features para predicción (última fila)
        features = features_df.iloc[-1].to_dict()
        
        # Preparar features para el modelo (solo las numéricas)
        feature_names = feature_engineering.get_feature_names()
        X = [[features.get(f, 0) for f in feature_names]]
        
        # Hacer predicción
        prediction = model_service.predict(X)
        probability = model_service.predict_proba(X)
        
        risk_level = "alto" if prediction[0] == 1 else "bajo"
        risk_score = probability[0][1] if len(probability[0]) > 1 else 0.5
        
        # Calcular confianza (basada en la diferencia entre probabilidades)
        confidence = abs(probability[0][1] - probability[0][0]) if len(probability[0]) > 1 else 0.5
        
        return PredictionResponse(
            student_id=request.student_id,
            course_id=request.course_id,
            risk_level=risk_level,
            risk_score=round(risk_score, 3),
            features={k: round(v, 3) if isinstance(v, float) else v for k, v in features.items()},
            confidence=round(confidence, 3)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al predecir: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al hacer la predicción: {str(e)}"
        )


@app.get("/predict/batch")
async def predict_batch_students(course_id: int):
    """
    Predice el riesgo académico de todos los estudiantes en un curso
    """
    try:
        # Verificar que el modelo esté cargado
        if not model_service.is_model_loaded():
            if not model_service.load_model():
                raise HTTPException(
                    status_code=503,
                    detail="El modelo no está entrenado. Por favor, entrena el modelo primero con /train"
                )
        
        # Obtener todos los estudiantes del curso
        students_data = data_service.get_course_students_data(course_id=course_id)
        
        if students_data is None or students_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron estudiantes en el curso {course_id}"
            )
        
        # Calcular features para todos los estudiantes
        features_df = feature_engineering.calculate_features(students_data)
        
        if features_df.empty:
            return []
        
        # Preparar features para predicción
        feature_names = feature_engineering.get_feature_names()
        X = features_df[feature_names].values
        
        # Hacer predicciones
        predictions = model_service.predict(X)
        probabilities = model_service.predict_proba(X)
        
        # Construir respuesta
        results = []
        for idx, (_, row) in enumerate(features_df.iterrows()):
            student_id = int(row.get('student_id', 0))
            risk_level = "alto" if predictions[idx] == 1 else "bajo"
            risk_score = probabilities[idx][1] if len(probabilities[idx]) > 1 else 0.5
            confidence = abs(probabilities[idx][1] - probabilities[idx][0]) if len(probabilities[idx]) > 1 else 0.5
            
            results.append({
                "student_id": student_id,
                "course_id": course_id,
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "features": {k: round(v, 3) if isinstance(v, float) else v 
                            for k, v in row.to_dict().items()},
                "confidence": round(confidence, 3)
            })
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en predicción batch: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al hacer la predicción batch: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

