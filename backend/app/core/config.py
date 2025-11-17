# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # ... (otras variables) ...

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173" # Añade esta por si acaso
    ]
    
    # --- VARIABLES GLOBALES DE LA APLICACIÓN ---
    PROJECT_NAME: str = "Plataforma Académica Inteligente PAI"
    API_V1_STR: str = "/api/v1" # O déjalo como "" si no quieres prefijo /api/v1
    
    # --- CONFIGURACIÓN DE CORS ---
    # Los orígenes que tienen permitido hacer solicitudes al backend
    # Aquí puedes añadir http://localhost:5173 para tu frontend de desarrollo
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"] 
    
    # --- VARIABLES DE BASE DE DATOS ---
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5432/pai_db" # ¡Asegúrate que esta sea tu URL!
    
    # --- VARIABLES DE SEGURIDAD ---
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True # Las variables de entorno son sensibles a mayúsculas/minúsculas

settings = Settings()