"""
Feature Engineering para el modelo de ML
Calcula las features necesarias para predecir el riesgo académico
"""

import pandas as pd
import numpy as np
from datetime import datetime


class FeatureEngineering:
    """Clase para calcular features a partir de datos históricos"""
    
    def __init__(self):
        self.feature_names = [
            'submission_delay_rate',  # Tasa de retraso en entregas
            'non_submission_rate',     # Tasa de no entrega
            'average_grade',           # Promedio de notas
            'grade_variability'        # Variabilidad de notas (desviación estándar)
        ]
    
    def get_feature_names(self) -> list:
        """Retorna la lista de nombres de features"""
        return self.feature_names
    
    def calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula las features para cada estudiante-curso
        
        Args:
            data: DataFrame con columnas: student_id, course_id, task_id, 
                  due_date, submitted_at, grade, etc.
        
        Returns:
            DataFrame con una fila por estudiante-curso y las features calculadas
        """
        if data.empty:
            return pd.DataFrame()
        
        # Convertir fechas a datetime si son strings
        date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
        for col in date_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col])
        
        # Agrupar por estudiante y curso
        grouped = data.groupby(['student_id', 'course_id'])
        
        results = []
        
        for (student_id, course_id), group in grouped:
            features = self._calculate_student_course_features(
                student_id, course_id, group
            )
            if features:
                results.append(features)
        
        if not results:
            return pd.DataFrame()
        
        df_features = pd.DataFrame(results)
        return df_features
    
    def _calculate_student_course_features(
        self, 
        student_id: int, 
        course_id: int, 
        group: pd.DataFrame
    ) -> dict:
        """
        Calcula las features para un estudiante específico en un curso específico
        """
        # 1. Tasa de retraso en entregas (submission_delay_rate)
        # Calcula cuántas entregas fueron tardías vs total de entregas
        delay_rate = 0.0
        if not group.empty and 'submitted_at' in group.columns and 'due_date' in group.columns:
            # Filtrar solo entregas con fecha de entrega válida
            valid_submissions = group[
                (group['submitted_at'].notna()) & 
                (group['due_date'].notna())
            ]
            
            if not valid_submissions.empty:
                # Calcular días de retraso (negativo = a tiempo, positivo = tardío)
                delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
                late_submissions = (delays > 0).sum()
                total_submissions = len(valid_submissions)
                delay_rate = late_submissions / total_submissions if total_submissions > 0 else 0.0
            else:
                delay_rate = 1.0  # Si no hay entregas, considerar como 100% retraso
        
        # 2. Tasa de no entrega (non_submission_rate)
        # Calculamos cuántas tareas no fueron entregadas vs total de tareas
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique()
        
        if total_tasks == 0:
            non_submission_rate = 1.0
        else:
            non_submission_rate = 1.0 - (submitted_tasks / total_tasks)
        
        # Asegurar que esté en el rango [0, 1]
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
        # Desviación estándar de las notas
        if grades.empty or len(grades) < 2:
            grade_variability = 0.0
        else:
            grade_std = grades.std()
            # Normalizar (asumiendo que la desviación máxima sería ~3.0 en escala 1-7)
            grade_variability = min(grade_std / 3.0, 1.0)
        
        return {
            'student_id': student_id,
            'course_id': course_id,
            'submission_delay_rate': delay_rate,
            'non_submission_rate': non_submission_rate,
            'average_grade': average_grade,
            'grade_variability': grade_variability
        }
    
    def calculate_target_variable(self, features_df: pd.DataFrame) -> pd.Series:
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

