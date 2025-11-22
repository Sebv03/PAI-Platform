"""
Script para exportar los datos históricos de la base de datos a CSV
Este CSV será el mismo que usa la plataforma para entrenar el modelo ML
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.config import settings


def export_historical_data_to_csv():
    """
    Exporta los datos históricos de la base de datos a CSV.
    Usa la misma query que el ML service para obtener los datos.
    """
    print("=" * 60)
    print("EXPORTANDO DATOS HISTORICOS A CSV")
    print("=" * 60)
    print()
    
    # Crear engine de base de datos
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    
    try:
        # Query exacta que usa el ML service (de data_service.py)
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
                s.grade
            FROM tasks t
            INNER JOIN enrollments e ON t.course_id = e.course_id
            LEFT JOIN submissions s ON s.task_id = t.id AND s.student_id = e.student_id
            ORDER BY e.student_id, t.course_id, t.due_date
        """)
        
        print("Obteniendo datos de la base de datos...")
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("ERROR: No hay datos en la base de datos.")
            print("Por favor, ejecuta primero el script populate_historical_data.py")
            return
        
        # Crear directorio si no existe
        output_dir = "datasets"
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar CSV
        output_path = os.path.join(output_dir, "historical_dataset.csv")
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        # Estadísticas
        print("Dataset exportado exitosamente")
        print()
        print("Estadisticas del Dataset:")
        print(f"   - Total registros: {len(df)}")
        print(f"   - Estudiantes unicos: {df['student_id'].nunique()}")
        print(f"   - Cursos unicos: {df['course_id'].nunique()}")
        print(f"   - Tareas unicas: {df['task_id'].nunique()}")
        print(f"   - Entregas realizadas: {df['submission_id'].notna().sum()}")
        print(f"   - Sin entregar: {df['submission_id'].isna().sum()}")
        
        if df['submission_id'].notna().sum() > 0:
            tasa_entrega = df['submission_id'].notna().sum() / len(df) * 100
            print(f"   - Tasa de entrega: {tasa_entrega:.2f}%")
        
        if df['grade'].notna().any():
            grades = df[df['grade'].notna()]['grade']
            print(f"   - Notas promedio: {grades.mean():.2f}")
            print(f"   - Notas min/max: {grades.min():.2f} / {grades.max():.2f}")
        
        print()
        print(f"Archivo guardado en: {output_path}")
        print()
        print("Estructura del CSV (primeras 10 filas):")
        print(df.head(10).to_string())
        print()
        print("Listo! Puedes usar este CSV en Google Colab o en el proyecto local.")
        print()
        print("NOTA: Este CSV contiene los mismos datos que usa la plataforma")
        print("      para entrenar el modelo ML.")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()


if __name__ == "__main__":
    export_historical_data_to_csv()

