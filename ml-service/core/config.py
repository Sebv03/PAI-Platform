"""
Configuración del microservicio ML
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PAI ML Service"
    
    # Base de datos (misma que el backend principal)
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5433/pai_db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Modelo ML
    MODEL_PATH: str = "models/risk_prediction_model.pkl"
    MODEL_DIR: str = "models"
    
    # Threshold para clasificación de riesgo
    RISK_THRESHOLD: float = 0.5
    
    class Config:
        case_sensitive = True


settings = Settings()

