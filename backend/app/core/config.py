# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, AnyHttpUrl
from typing import List, Optional, Union, Any

class Settings(BaseSettings):
    # Configuración de Pydantic v2: Carga desde .env, sensible a mayúsculas, ignora extras
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Variables de la App
    PROJECT_NAME: str = "Plataforma Académica Inteligente PAI"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"] 

    # --- CORRECCIÓN DE HOST/SERVER ---
    POSTGRES_SERVER: str # <-- ¡RENOMBRADO! Coincide con el .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int # <-- Cambiado a 'int' para mejor validación

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str):
            return v
        
        # Pydantic v2 usa info.data
        data = info.data
            
        # Construye la URL usando las variables del .env
        return (
            f"postgresql://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}@"
            f"{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}" # <-- ¡RENOMBRADO!
        )
    # -----------------------------------

    # Variables de Seguridad
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

settings = Settings()