# Script para crear las tablas de announcements y comments
# Ejecuta este script una vez para crear las tablas en la base de datos

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models.announcement import Announcement
from app.models.comment import Comment

def create_forum_tables():
    """Crea las tablas de announcements y comments en la base de datos"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creando tablas de foro (announcements y comments)...")
    Base.metadata.create_all(bind=engine, tables=[Announcement.__table__, Comment.__table__])
    print("Tablas de foro creadas exitosamente.")

if __name__ == "__main__":
    create_forum_tables()


