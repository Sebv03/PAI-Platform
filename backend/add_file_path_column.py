# Script para agregar la columna file_path a la tabla submissions
# Ejecuta este script una vez para actualizar la base de datos

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_file_path_column():
    """Agrega la columna file_path a la tabla submissions si no existe"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='submissions' AND column_name='file_path'
        """)
        result = conn.execute(check_query)
        
        if result.fetchone():
            print("La columna 'file_path' ya existe en la tabla 'submissions'.")
        else:
            # Agregar la columna
            alter_query = text("""
                ALTER TABLE submissions 
                ADD COLUMN file_path VARCHAR(500)
            """)
            conn.execute(alter_query)
            conn.commit()
            print("Columna 'file_path' agregada exitosamente a la tabla 'submissions'.")
    
    print("Migración completada.")

if __name__ == "__main__":
    add_file_path_column()


