"""
Script para calcular el target de manera independiente a las features normalizadas
Esto evita que el modelo "copie" la lógica de decisión
"""

import pandas as pd
import numpy as np


def calculate_target_from_raw_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el target usando datos RAW, antes de normalizar features.
    Esto evita data leakage (fuga de datos).
    
    Args:
        data: DataFrame con datos raw (task_id, course_id, student_id, 
              due_date, submitted_at, grade, etc.)
    
    Returns:
        DataFrame con student_id, course_id, risk (target)
    """
    # Convertir fechas
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])
    
    # Agrupar por estudiante y curso
    grouped = data.groupby(['student_id', 'course_id'])
    results = []
    
    for (student_id, course_id), group in grouped:
        # Calcular promedio REAL (no normalizado)
        grades = group[group['grade'].notna()]['grade']
        avg_grade = grades.mean() if not grades.empty else 0.0
        
        # Calcular tasa de no entrega REAL
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique()
        non_submission_rate = 1.0 - (submitted_tasks / total_tasks) if total_tasks > 0 else 1.0
        
        # Calcular riesgo usando valores REALES (no normalizados)
        # Riesgo alto si: promedio < 4.0 O tasa de no entrega > 0.5
        risk_high = (avg_grade < 4.0) or (non_submission_rate > 0.5)
        
        results.append({
            'student_id': student_id,
            'course_id': course_id,
            'risk': 1 if risk_high else 0,
            'avg_grade_raw': avg_grade,
            'non_submission_rate_raw': non_submission_rate
        })
    
    return pd.DataFrame(results)


def calculate_features_normalized(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula features normalizadas (sin calcular target).
    Separado del cálculo del target para evitar data leakage.
    """
    # Convertir fechas
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])
    
    grouped = data.groupby(['student_id', 'course_id'])
    results = []
    
    for (student_id, course_id), group in grouped:
        # 1. Tasa de retraso
        delay_rate = 0.0
        valid_submissions = group[(group['submitted_at'].notna()) & (group['due_date'].notna())]
        if not valid_submissions.empty:
            delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
            late_submissions = (delays > 0).sum()
            total_submissions = len(valid_submissions)
            delay_rate = late_submissions / total_submissions if total_submissions > 0 else 0.0
        else:
            delay_rate = 1.0
        
        # 2. Tasa de no entrega
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique()
        non_submission_rate = 1.0 - (submitted_tasks / total_tasks) if total_tasks > 0 else 1.0
        non_submission_rate = max(0.0, min(1.0, non_submission_rate))
        
        # 3. Promedio de notas (normalizado)
        grades = group[group['grade'].notna()]['grade']
        average_grade = (grades.mean() - 1.0) / 6.0 if not grades.empty else 0.0
        
        # 4. Variabilidad de notas
        if grades.empty or len(grades) < 2:
            grade_variability = 0.0
        else:
            grade_std = grades.std()
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


# Ejemplo de uso:
if __name__ == "__main__":
    print("Funciones para calcular features y target de manera separada")
    print("Esto evita que el modelo 'copie' la lógica de decisión")
    print()
    print("Uso:")
    print("  1. Cargar datos raw desde CSV")
    print("  2. Calcular features normalizadas (X)")
    print("  3. Calcular target desde datos raw (y)")
    print("  4. Entrenar modelo con X e y")

