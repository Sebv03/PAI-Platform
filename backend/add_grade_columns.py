# Script para agregar las columnas grade y feedback a la tabla submissions
# Ejecuta este script una vez para actualizar la base de datos

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_grade_columns():
    """Agrega las columnas grade y feedback a la tabla submissions si no existen"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar y agregar columna grade
        check_grade = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='submissions' AND column_name='grade'
        """)
        result = conn.execute(check_grade)
        
        if result.fetchone():
            print("La columna 'grade' ya existe en la tabla 'submissions'.")
        else:
            alter_grade = text("""
                ALTER TABLE submissions 
                ADD COLUMN grade REAL
            """)
            conn.execute(alter_grade)
            conn.commit()
            print("Columna 'grade' agregada exitosamente.")
        
        # Verificar y agregar columna feedback
        check_feedback = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='submissions' AND column_name='feedback'
        """)
        result = conn.execute(check_feedback)
        
        if result.fetchone():
            print("La columna 'feedback' ya existe en la tabla 'submissions'.")
        else:
            alter_feedback = text("""
                ALTER TABLE submissions 
                ADD COLUMN feedback TEXT
            """)
            conn.execute(alter_feedback)
            conn.commit()
            print("Columna 'feedback' agregada exitosamente.")
    
    print("Migración completada.")

if __name__ == "__main__":
    add_grade_columns()


