"""
Script para exportar datos históricos completos a CSV incluyendo perfiles de estudiantes
Este CSV incluye todas las features necesarias para entrenar el modelo ML
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.config import settings

# Crear engine
engine = create_engine(settings.DATABASE_URL)

def export_historical_data_with_profiles():
    """
    Exporta todos los datos históricos a CSV incluyendo perfiles de estudiantes
    """
    print("=" * 60)
    print("EXPORTANDO DATOS HISTORICOS CON PERFILES")
    print("=" * 60)
    print()
    
    # Query que obtiene todos los datos necesarios incluyendo perfiles
    query = text("""
        SELECT 
            t.id as task_id,
            t.course_id,
            t.due_date,
            t.created_at as task_created_at,
            e.student_id,
            e.enrollment_date,
            s.id as submission_id,
            s.submitted_at,
            s.grade,
            -- Perfil del estudiante (features del cuestionario)
            sp.motivation,
            sp.available_time,
            sp.sleep_hours,
            sp.study_hours,
            sp.enjoyment_studying,
            sp.study_place_tranquility,
            sp.academic_pressure,
            sp.gender
        FROM tasks t
        INNER JOIN enrollments e ON t.course_id = e.course_id
        LEFT JOIN submissions s ON s.task_id = t.id AND s.student_id = e.student_id
        LEFT JOIN student_profiles sp ON sp.student_id = e.student_id
        ORDER BY e.student_id, t.course_id, t.due_date
    """)
    
    try:
        print("Obteniendo datos de la base de datos...")
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("ERROR: No se encontraron datos en la base de datos.")
            return
        
        print(f"[OK] Datos obtenidos: {len(df)} registros")
        print(f"[OK] Estudiantes únicos: {df['student_id'].nunique()}")
        print(f"[OK] Cursos únicos: {df['course_id'].nunique()}")
        print(f"[OK] Tareas únicas: {df['task_id'].nunique()}")
        print()
        
        # Estadísticas de perfiles
        profiles_count = df['motivation'].notna().sum()
        print(f"[OK] Registros con perfil de estudiante: {profiles_count}")
        
        if profiles_count == 0:
            print("ADVERTENCIA: No se encontraron perfiles de estudiantes.")
            print("Ejecuta primero: python populate_student_profiles.py")
            print()
        
        # Guardar CSV
        output_file = "datasets/historical_dataset_with_profiles.csv"
        output_dir = Path("datasets")
        output_dir.mkdir(exist_ok=True)
        
        print(f"Guardando CSV en: {output_file}")
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print()
        print("=" * 60)
        print("EXPORTACION COMPLETADA")
        print("=" * 60)
        print()
        print(f"Archivo guardado en: {output_file}")
        print(f"Total de registros: {len(df)}")
        print(f"Columnas: {len(df.columns)}")
        print()
        print("Columnas incluidas:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    export_historical_data_with_profiles()

