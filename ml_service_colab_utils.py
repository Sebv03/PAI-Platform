"""
Utilidades para el notebook de Google Colab
Replica la lógica del modelo ML de PAI Platform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


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


def calculate_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula las features para cada estudiante-curso.
    Replica la lógica del archivo feature_engineering.py del proyecto.
    """
    # Convertir fechas a datetime si son strings
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])
    
    # Agrupar por estudiante y curso
    grouped = data.groupby(['student_id', 'course_id'])
    
    results = []
    
    for (student_id, course_id), group in grouped:
        # 1. Tasa de retraso en entregas (submission_delay_rate)
        delay_rate = 0.0
        valid_submissions = group[
            (group['submitted_at'].notna()) & 
            (group['due_date'].notna())
        ]
        
        if not valid_submissions.empty:
            # Calcular días de retraso
            delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
            late_submissions = (delays > 0).sum()
            total_submissions = len(valid_submissions)
            delay_rate = late_submissions / total_submissions if total_submissions > 0 else 0.0
        else:
            delay_rate = 1.0  # Si no hay entregas, considerar como 100% retraso
        
        # 2. Tasa de no entrega (non_submission_rate)
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique()
        
        if total_tasks == 0:
            non_submission_rate = 1.0
        else:
            non_submission_rate = 1.0 - (submitted_tasks / total_tasks)
        
        non_submission_rate = max(0.0, min(1.0, non_submission_rate))
        
        # 3. Promedio de notas (average_grade)
        grades = group[group['grade'].notna()]['grade']
        if grades.empty:
            average_grade = 0.0
        else:
            average_grade = grades.mean()
            # Normalizar a escala 0-1 (asumiendo que las notas van de 1.0 a 7.0)
            average_grade = (average_grade - 1.0) / 6.0
        
        # 4. Variabilidad de notas (grade_variability)
        if grades.empty or len(grades) < 2:
            grade_variability = 0.0
        else:
            grade_std = grades.std()
            # Normalizar (asumiendo que la desviación máxima sería ~3.0 en escala 1-7)
            grade_variability = min(grade_std / 3.0, 1.0)
        
        results.append({
            'student_id': student_id,
            'course_id': course_id,
            'submission_delay_rate': delay_rate,
            'non_submission_rate': non_submission_rate,
            'average_grade': average_grade,
            'grade_variability': grade_variability
        })
    
    return pd.DataFrame(results)
    
    return pd.DataFrame(results)


def calculate_target(features_df: pd.DataFrame) -> pd.Series:
    """
    Calcula la variable objetivo (Y) basada en las features.
    Riesgo alto (1) si: promedio < 4.0 (en escala 1-7) o tasa de no entrega > 0.5
    """
    # Desnormalizar average_grade para comparar con 4.0
    average_grade_original = features_df['average_grade'] * 6.0 + 1.0
    
    # Definir riesgo alto
    risk_high = (
        (average_grade_original < 4.0) | 
        (features_df['non_submission_rate'] > 0.5)
    )
    
    return risk_high.astype(int)

