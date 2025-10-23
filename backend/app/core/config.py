# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://sebahenriquez@localhost:5433/pai_db"

    # --- AÑADIR ESTAS LÍNEAS ---
    # Una cadena aleatoria y secreta para firmar los tokens JWT.
    # En un proyecto real, esto NUNCA debe estar en el código. Se carga desde una variable de entorno.
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # El token será válido por 30 minutos

settings = Settings()