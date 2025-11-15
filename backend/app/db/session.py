# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # ¡Aun la necesitamos para otras configs!

# --- CAMBIO AQUÍ ---
# Comenta la línea que usa settings.DATABASE_URL
# DATABASE_URL = settings.DATABASE_URL

# Define la URL directamente aquí con tus datos:
# Asegúrate que 'TU_CONTRASEÑA_REAL' sea la contraseña correcta de tu usuario 'postgres'
DATABASE_URL_HARDCODED = "postgresql://postgres:123456@localhost:5433/pai_db" # <--- ¡VERIFICAR ESTO!

engine = create_engine(DATABASE_URL_HARDCODED, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()