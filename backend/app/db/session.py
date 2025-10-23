# backend/app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Creamos el motor de base de datos.
# El engine es el punto de entrada a la base de datos.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Creamos una fábrica de sesiones.
# Cada instancia de SessionLocal será una nueva sesión de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)