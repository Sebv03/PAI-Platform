# backend/app/core/config.py
from pydantic_settings import BaseSettings # Asegúrate de usar pydantic_settings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Plataforma Académica Inteligente PAI"
    API_V1_STR: str = "/api/v1"
    
    # Asegúrate que tu frontend corra en este puerto para CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"] 
    
    # --- ¡CRÍTICO! Tu URL de Base de Datos para PostgreSQL ---
    # Asegúrate que 'postgres:123456' sean tus credenciales y '5433' tu puerto
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5433/pai_db"
    
    # --- ¡CRÍTICO! Claves de Seguridad ---
    # Puedes generar una nueva: import secrets; secrets.token_hex(32)
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256" # Deja este valor, es estándar
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- Directorio para almacenar archivos subidos ---
    UPLOAD_DIR: str = "uploads/submissions"

    class Config:
        case_sensitive = True

settings = Settings()