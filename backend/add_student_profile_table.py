"""
Script para crear la tabla student_profiles en la base de datos
"""

import sys
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models.student_profile import StudentProfile

# Crear engine
engine = create_engine(settings.DATABASE_URL)

def create_table():
    """Crea la tabla student_profiles"""
    print("=" * 60)
    print("CREANDO TABLA STUDENT_PROFILES")
    print("=" * 60)
    print()
    
    try:
        # Crear la tabla
        StudentProfile.__table__.create(bind=engine, checkfirst=True)
        print("[OK] Tabla 'student_profiles' creada exitosamente")
        print()
        print("Columnas creadas:")
        print("  - id (PK)")
        print("  - student_id (FK -> users.id, UNIQUE)")
        print("  - motivation (Float, 1-10)")
        print("  - available_time (Float, 1-10)")
        print("  - sleep_hours (Float, 1-10)")
        print("  - study_hours (Float, 1-10)")
        print("  - enjoyment_studying (Float, 1-10)")
        print("  - study_place_tranquility (Float, 1-10)")
        print("  - academic_pressure (Float, 1-10)")
        print("  - gender (String)")
        print("  - created_at (DateTime)")
        print("  - updated_at (DateTime)")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_table()

