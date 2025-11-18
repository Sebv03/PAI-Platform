# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Importa la configuración

# ¡Esta es la línea clave! Usa la URL que definimos en config.py
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para los endpoints (la usa deps.py)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()