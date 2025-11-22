"""
Script para agregar 1000 estudiantes adicionales directamente al CSV histórico
Genera datos sintéticos y los agrega al CSV sin modificar la base de datos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import random
import os

# Configuración
NUEVOS_ESTUDIANTES = 1000
CSV_INPUT = "datasets/historical_dataset.csv"
CSV_OUTPUT = "datasets/historical_dataset_updated.csv"  # Archivo nuevo primero

# Nombres para generar estudiantes
FIRST_NAMES = [
    "Alejandro", "Andrés", "Antonio", "Carlos", "Diego", "Fernando", "Gabriel",
    "Gonzalo", "Ignacio", "Javier", "Jorge", "José", "Juan", "Luis", "Manuel",
    "Miguel", "Pablo", "Pedro", "Rafael", "Roberto", "Sergio", "Tomás",
    "Ana", "Andrea", "Camila", "Carolina", "Catalina", "Cecilia", "Claudia",
    "Daniela", "Elena", "Francisca", "Gabriela", "Isabella", "Javiera",
    "Laura", "María", "Martina", "Natalia", "Paola", "Patricia", "Sofía",
    "Valentina", "Verónica", "Viviana"
]

LAST_NAMES = [
    "Aguilar", "Alvarado", "Álvarez", "Andrade", "Araya", "Arévalo", "Arias",
    "Barrera", "Benítez", "Bravo", "Cabrera", "Calderón", "Campos", "Cárdenas",
    "Carvajal", "Castillo", "Castro", "Chávez", "Contreras", "Correa", "Cortés",
    "Cruz", "Díaz", "Dominguez", "Espinoza", "Fernández", "Figueroa", "Flores",
    "Fuentes", "Gallardo", "García", "Gómez", "González", "Guerrero", "Gutiérrez",
    "Guzmán", "Hernández", "Herrera", "Jiménez", "Lara", "León", "López",
    "Maldonado", "Martínez", "Medina", "Mendoza", "Morales", "Moreno", "Muñoz",
    "Navarro", "Núñez", "Olivares", "Ortega", "Ortiz", "Paredes", "Parra",
    "Pérez", "Pizarro", "Ramírez", "Ramos", "Reyes", "Rivera", "Rodríguez",
    "Rojas", "Romero", "Ruiz", "Sánchez", "Soto", "Torres", "Valdez", "Vargas",
    "Vásquez", "Vega", "Velásquez", "Vera", "Villalobos", "Zamora", "Zúñiga"
]


def generate_student_name(index):
    """Genera un nombre único para un estudiante"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Agregar número para hacer único
    full_name = f"{first_name} {last_name}"
    if index > 100:
        full_name = f"{first_name} {last_name} {index % 100}"
    
    return first_name, last_name, full_name


def generate_additional_data(existing_df, num_students=1000):
    """
    Genera datos para estudiantes adicionales basándose en el CSV existente
    """
    print(f"Generando datos para {num_students} estudiantes adicionales...")
    
    # Obtener información del dataset existente
    max_student_id = existing_df['student_id'].max()
    course_ids = existing_df['course_id'].unique()
    task_info = existing_df.groupby(['course_id', 'task_id']).agg({
        'due_date': 'first',
        'task_created_at': 'first'
    }).reset_index()
    
    # Si las fechas son strings, convertirlas usando ISO8601
    if not pd.api.types.is_datetime64_any_dtype(existing_df['due_date']):
        existing_df['due_date'] = pd.to_datetime(existing_df['due_date'], format='ISO8601', errors='coerce')
        existing_df['task_created_at'] = pd.to_datetime(existing_df['task_created_at'], format='ISO8601', errors='coerce')
        existing_df['enrollment_date'] = pd.to_datetime(existing_df['enrollment_date'], format='ISO8601', errors='coerce')
        if 'submitted_at' in existing_df.columns:
            existing_df['submitted_at'] = pd.to_datetime(existing_df['submitted_at'], format='ISO8601', errors='coerce')
    
    # Asegurar que task_info también tenga fechas como datetime
    task_info['due_date'] = pd.to_datetime(task_info['due_date'], format='ISO8601', errors='coerce')
    task_info['task_created_at'] = pd.to_datetime(task_info['task_created_at'], format='ISO8601', errors='coerce')
    
    # Base de fechas
    base_date = datetime.now(timezone.utc)
    
    # Obtener el último task_id y submission_id
    max_task_id = existing_df['task_id'].max()
    max_submission_id = existing_df['submission_id'].max() if existing_df['submission_id'].notna().any() else 0
    
    new_data = []
    current_student_id = max_student_id + 1
    current_submission_id = int(max_submission_id) + 1 if not pd.isna(max_submission_id) else 1
    
    # Semilla para reproducibilidad
    np.random.seed(42)
    random.seed(42)
    
    print("Procesando estudiantes...")
    for student_idx in range(num_students):
        student_id = current_student_id + student_idx
        first_name, last_name, full_name = generate_student_name(student_idx)
        
        # Cada estudiante se inscribe en 1-3 cursos
        num_courses = random.randint(1, min(3, len(course_ids)))
        selected_courses = random.sample(list(course_ids), num_courses)
        
        enrollment_date = base_date - timedelta(days=random.randint(90, 120))
        
        for course_id in selected_courses:
            # Obtener tareas del curso
            course_tasks = task_info[task_info['course_id'] == course_id]
            
            if course_tasks.empty:
                continue
            
            for _, task_row in course_tasks.iterrows():
                task_id = task_row['task_id']
                due_date = pd.to_datetime(task_row['due_date']) if not pd.api.types.is_datetime64_any_dtype(type(task_row['due_date'])) else task_row['due_date']
                task_created_at = pd.to_datetime(task_row['task_created_at']) if not pd.api.types.is_datetime64_any_dtype(type(task_row['task_created_at'])) else task_row['task_created_at']
                
                # Determinar perfil de riesgo (30% alto riesgo, 70% bajo riesgo)
                is_high_risk = np.random.random() < 0.3
                
                if is_high_risk:
                    submission_prob = np.random.uniform(0.3, 0.7)
                    late_submission_prob = 0.6
                    avg_grade = np.random.uniform(2.5, 4.0)
                else:
                    submission_prob = np.random.uniform(0.7, 0.95)
                    late_submission_prob = 0.2
                    avg_grade = np.random.uniform(4.5, 6.5)
                
                # Decidir si entregó
                will_submit = np.random.random() < submission_prob
                
                if will_submit:
                    # Calcular fecha de entrega
                    is_late = np.random.random() < late_submission_prob
                    
                    if is_late:
                        days_late = np.random.randint(1, 7)
                        submitted_at = due_date + timedelta(days=days_late)
                    else:
                        days_early = np.random.randint(-2, 1)
                        submitted_at = due_date + timedelta(days=days_early)
                    
                    # Asignar nota
                    grade_variability = np.random.uniform(0.5, 1.5)
                    grade = max(1.0, min(7.0, np.random.normal(avg_grade, grade_variability)))
                    grade = round(grade, 1)
                    
                    new_data.append({
                        'task_id': task_id,
                        'course_id': course_id,
                        'student_id': student_id,
                        'task_created_at': task_created_at,
                        'due_date': due_date,
                        'enrollment_date': enrollment_date,
                        'submission_id': current_submission_id,
                        'submitted_at': submitted_at,
                        'grade': grade
                    })
                    
                    current_submission_id += 1
                else:
                    # No entregó
                    new_data.append({
                        'task_id': task_id,
                        'course_id': course_id,
                        'student_id': student_id,
                        'task_created_at': task_created_at,
                        'due_date': due_date,
                        'enrollment_date': enrollment_date,
                        'submission_id': None,
                        'submitted_at': None,
                        'grade': None
                    })
        
        if (student_idx + 1) % 100 == 0:
            print(f"  Procesados {student_idx + 1}/{num_students} estudiantes...")
    
    return pd.DataFrame(new_data)


def main():
    """Función principal"""
    print("=" * 60)
    print("AGREGAR 1000 ESTUDIANTES AL CSV HISTORICO")
    print("=" * 60)
    print()
    
    # Verificar que existe el CSV
    if not os.path.exists(CSV_INPUT):
        print(f"ERROR: No se encuentra el archivo {CSV_INPUT}")
        print("Por favor, ejecuta primero: python export_historical_data_to_csv.py")
        return
    
    # Leer CSV existente
    print(f"Leyendo CSV existente: {CSV_INPUT}")
    try:
        existing_df = pd.read_csv(CSV_INPUT)
        print(f"  - Registros existentes: {len(existing_df)}")
        print(f"  - Estudiantes existentes: {existing_df['student_id'].nunique()}")
        print(f"  - Cursos: {existing_df['course_id'].nunique()}")
        print()
    except Exception as e:
        print(f"ERROR al leer CSV: {e}")
        return
    
    # Generar datos adicionales
    new_df = generate_additional_data(existing_df, num_students=NUEVOS_ESTUDIANTES)
    print()
    print(f"Generados {len(new_df)} registros adicionales")
    print()
    
    # Combinar datos
    print("Combinando datos...")
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Ordenar por student_id, course_id, due_date
    combined_df = combined_df.sort_values(['student_id', 'course_id', 'due_date']).reset_index(drop=True)
    
    # Guardar CSV
    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Guardando CSV actualizado en: {CSV_OUTPUT}")
    combined_df.to_csv(CSV_OUTPUT, index=False, encoding='utf-8')
    
    # Estadísticas finales
    print()
    print("=" * 60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Estadisticas del Dataset Actualizado:")
    print(f"   - Total registros: {len(combined_df)}")
    print(f"   - Estudiantes unicos: {combined_df['student_id'].nunique()}")
    print(f"   - Cursos unicos: {combined_df['course_id'].nunique()}")
    print(f"   - Tareas unicas: {combined_df['task_id'].nunique()}")
    print(f"   - Entregas realizadas: {combined_df['submission_id'].notna().sum()}")
    print(f"   - Sin entregar: {combined_df['submission_id'].isna().sum()}")
    
    if combined_df['submission_id'].notna().sum() > 0:
        tasa_entrega = combined_df['submission_id'].notna().sum() / len(combined_df) * 100
        print(f"   - Tasa de entrega: {tasa_entrega:.2f}%")
    
    if combined_df['grade'].notna().any():
        grades = combined_df[combined_df['grade'].notna()]['grade']
        print(f"   - Notas promedio: {grades.mean():.2f}")
        print(f"   - Notas min/max: {grades.min():.2f} / {grades.max():.2f}")
    
    print()
    print(f"Archivo guardado en: {CSV_OUTPUT}")
    print()
    print("El CSV ahora incluye los 1000 estudiantes adicionales.")
    print("Puedes usar este CSV en Google Colab o en el proyecto local.")
    print()


if __name__ == "__main__":
    main()

