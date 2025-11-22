"""
Script para generar un dataset de prueba en formato CSV
Este CSV puede usarse tanto en el notebook de Colab como en el proyecto local
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_synthetic_data(
    n_students=200,
    n_courses=10,
    tasks_per_course=8,
    random_seed=42
):
    """
    Genera un dataset sintético de estudiantes, cursos, tareas y entregas.
    
    Args:
        n_students: Número de estudiantes
        n_courses: Número de cursos
        tasks_per_course: Número de tareas por curso
        random_seed: Semilla para reproducibilidad
    
    Returns:
        DataFrame con datos sintéticos
    """
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    data = []
    base_date = datetime(2024, 1, 15)
    
    # Generar inscripciones de estudiantes en cursos
    enrollments = []
    for student_id in range(1, n_students + 1):
        # Cada estudiante está inscrito en 1-3 cursos
        n_courses_student = np.random.randint(1, 4)
        student_courses = np.random.choice(
            range(1, n_courses + 1), 
            size=n_courses_student, 
            replace=False
        )
        
        for course_id in student_courses:
            enrollment_date = base_date + timedelta(days=np.random.randint(-30, 0))
            enrollments.append({
                'student_id': student_id,
                'course_id': course_id,
                'enrollment_date': enrollment_date
            })
    
    # Generar tareas para cada curso
    tasks = []
    for course_id in range(1, n_courses + 1):
        for task_num in range(1, tasks_per_course + 1):
            task_id = (course_id - 1) * tasks_per_course + task_num
            task_created_at = base_date + timedelta(days=(task_num - 1) * 14)
            due_date = task_created_at + timedelta(days=7)
            
            tasks.append({
                'task_id': task_id,
                'course_id': course_id,
                'task_created_at': task_created_at,
                'due_date': due_date
            })
    
    # Generar datos de entregas
    for enrollment in enrollments:
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        enrollment_date = enrollment['enrollment_date']
        
        # Obtener tareas del curso
        course_tasks = [t for t in tasks if t['course_id'] == course_id]
        
        # Determinar perfil del estudiante (30% alto riesgo, 70% bajo riesgo)
        is_high_risk = np.random.random() < 0.3
        
        for task in course_tasks:
            task_id = task['task_id']
            due_date = task['due_date']
            
            # Probabilidad de entrega basada en perfil de riesgo
            if is_high_risk:
                submission_prob = np.random.uniform(0.3, 0.7)  # Menos entregas
                late_submission_prob = 0.6  # Más entregas tardías
                avg_grade = np.random.uniform(2.5, 4.0)  # Notas más bajas
            else:
                submission_prob = np.random.uniform(0.7, 0.95)  # Más entregas
                late_submission_prob = 0.2  # Menos entregas tardías
                avg_grade = np.random.uniform(4.5, 6.5)  # Notas más altas
            
            # Decidir si entregó
            submitted = np.random.random() < submission_prob
            
            if submitted:
                # Calcular fecha de entrega (puede ser tardía)
                is_late = np.random.random() < late_submission_prob
                
                if is_late:
                    # Entrega tardía: 1-14 días después de la fecha límite
                    days_late = np.random.randint(1, 15)
                    submitted_at = due_date + timedelta(days=days_late)
                else:
                    # Entrega a tiempo: hasta 2 días antes o en la fecha límite
                    days_early = np.random.randint(-2, 1)
                    submitted_at = due_date + timedelta(days=days_early)
                
                # Asignar nota (basada en perfil de riesgo con variabilidad)
                grade_variability = np.random.uniform(0.5, 1.5)
                grade = max(1.0, min(7.0, np.random.normal(avg_grade, grade_variability)))
                grade = round(grade, 2)
                
                submission_id = len([d for d in data if d.get('submission_id')]) + 1
                
                data.append({
                    'task_id': task_id,
                    'course_id': course_id,
                    'student_id': student_id,
                    'task_created_at': task['task_created_at'],
                    'due_date': due_date,
                    'enrollment_date': enrollment_date,
                    'submission_id': submission_id,
                    'submitted_at': submitted_at,
                    'grade': grade
                })
            else:
                # No entregó
                data.append({
                    'task_id': task_id,
                    'course_id': course_id,
                    'student_id': student_id,
                    'task_created_at': task['task_created_at'],
                    'due_date': due_date,
                    'enrollment_date': enrollment_date,
                    'submission_id': None,
                    'submitted_at': None,
                    'grade': None
                })
    
    return pd.DataFrame(data)


def main():
    """Función principal para generar el CSV"""
    print("=" * 60)
    print("GENERANDO DATASET DE PRUEBA")
    print("=" * 60)
    print()
    
    # Generar datos
    print("Generando datos sintéticos...")
    df = generate_synthetic_data(
        n_students=200,
        n_courses=10,
        tasks_per_course=8,
        random_seed=42
    )
    
    # Crear directorio si no existe
    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar CSV
    output_path = os.path.join(output_dir, "test_dataset.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    # Estadísticas
    print("Dataset generado exitosamente")
    print()
    print("Estadisticas del Dataset:")
    print(f"   - Total registros: {len(df)}")
    print(f"   - Estudiantes unicos: {df['student_id'].nunique()}")
    print(f"   - Cursos unicos: {df['course_id'].nunique()}")
    print(f"   - Tareas unicas: {df['task_id'].nunique()}")
    print(f"   - Entregas realizadas: {df['submission_id'].notna().sum()}")
    print(f"   - Sin entregar: {df['submission_id'].isna().sum()}")
    print(f"   - Tasa de entrega: {df['submission_id'].notna().sum() / len(df) * 100:.2f}%")
    
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


if __name__ == "__main__":
    main()

