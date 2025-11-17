# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True, 
    # Añadir esta línea para sqlite si es el caso, pero no para postgres
    # connect_args={"check_same_thread": False} 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db(): # Esta función DEBE ser un generador
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()