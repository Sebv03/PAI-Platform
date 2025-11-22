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
        # Features predictivas (del cuestionario, disponibles al inicio del curso)
        # Estas son las features PRINCIPALES para predicción temprana
        self.profile_features = [
            'motivation',                # Motivación (1-10, normalizado 0-1)
            'available_time',            # Tiempo disponible (1-10, normalizado 0-1)
            'sleep_hours',               # Horas de sueño (1-10, normalizado 0-1)
            'study_hours',               # Horas de estudio (1-10, normalizado 0-1)
            'enjoyment_studying',        # Gusto por estudiar (1-10, normalizado 0-1)
            'study_place_tranquility',   # Tranquilidad del lugar (1-10, normalizado 0-1)
            'academic_pressure',         # Presión académica (1-10, normalizado 0-1)
            'gender_encoded'             # Género codificado (0, 0.5, 1)
        ]
        
        # Features transaccionales (requieren datos durante el curso)
        # Estas se completan con valores por defecto si no hay datos
        self.transactional_features = [
            'submission_delay_rate',  # Tasa de retraso en entregas (0-1)
            'non_submission_rate',     # Tasa de no entrega (0-1)
            'average_grade',           # Promedio de notas normalizado (0-1)
            'grade_variability'        # Variabilidad de notas normalizado (0-1)
        ]
        
        # Todas las features (predictivas primero para mayor importancia)
        self.feature_names = self.profile_features + self.transactional_features
    
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
        # FEATURES TRANSACCIONALES (pueden ser NaN si no hay datos del curso)
        # 1. Tasa de retraso en entregas (submission_delay_rate)
        delay_rate = 0.5  # Valor por defecto (neutral) si no hay datos
        if not group.empty and 'submitted_at' in group.columns and 'due_date' in group.columns:
            valid_submissions = group[
                (group['submitted_at'].notna()) & 
                (group['due_date'].notna())
            ]
            
            if not valid_submissions.empty:
                delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
                late_submissions = (delays > 0).sum()
                total_submissions = len(valid_submissions)
                delay_rate = late_submissions / total_submissions if total_submissions > 0 else 0.5
            elif 'task_id' in group.columns and len(group['task_id'].unique()) > 0:
                # Hay tareas pero no hay entregas aún
                delay_rate = 0.5  # Neutral hasta que haya entregas
        
        # 2. Tasa de no entrega (non_submission_rate)
        non_submission_rate = 0.5  # Valor por defecto
        total_tasks = len(group['task_id'].unique()) if 'task_id' in group.columns else 0
        if total_tasks > 0:
            submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique() if 'submission_id' in group.columns else 0
            non_submission_rate = 1.0 - (submitted_tasks / total_tasks)
            non_submission_rate = max(0.0, min(1.0, non_submission_rate))
        
        # 3. Promedio de notas (average_grade)
        average_grade = 0.5  # Valor por defecto (promedio medio normalizado)
        if 'grade' in group.columns:
            grades = group[group['grade'].notna()]['grade']
            if not grades.empty:
                avg = grades.mean()
                average_grade = (avg - 1.0) / 6.0  # Normalizar a 0-1
                average_grade = max(0.0, min(1.0, average_grade))
        
        # 4. Variabilidad de notas (grade_variability)
        grade_variability = 0.5  # Valor por defecto
        if 'grade' in group.columns:
            grades = group[group['grade'].notna()]['grade']
            if not grades.empty and len(grades) >= 2:
                grade_std = grades.std()
                grade_variability = min(grade_std / 3.0, 1.0)
        
        # Obtener datos del perfil del estudiante (si existen)
        # Estos datos vienen en todas las filas del grupo (son constantes por estudiante)
        first_row = group.iloc[0]
        
        # Features del perfil (normalizadas a 0-1, escala original 1-10)
        motivation = (first_row.get('motivation', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('motivation')) else 0.5
        available_time = (first_row.get('available_time', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('available_time')) else 0.5
        sleep_hours = (first_row.get('sleep_hours', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('sleep_hours')) else 0.5
        study_hours = (first_row.get('study_hours', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('study_hours')) else 0.5
        enjoyment_studying = (first_row.get('enjoyment_studying', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('enjoyment_studying')) else 0.5
        study_place_tranquility = (first_row.get('study_place_tranquility', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('study_place_tranquility')) else 0.5
        academic_pressure = (first_row.get('academic_pressure', 5.0) - 1.0) / 9.0 if pd.notna(first_row.get('academic_pressure')) else 0.5
        
        # Codificar género (one-hot encoding: masculino=0, femenino=1, otro=0.5)
        gender_val = first_row.get('gender', '')
        if pd.isna(gender_val) or gender_val == '':
            gender_encoded = 0.5  # Valor medio si no está especificado
        else:
            gender_str = str(gender_val).lower()
            if 'femenino' in gender_str or 'mujer' in gender_str or 'female' in gender_str:
                gender_encoded = 1.0
            elif 'masculino' in gender_str or 'hombre' in gender_str or 'male' in gender_str:
                gender_encoded = 0.0
            else:
                gender_encoded = 0.5  # Otro/no binario
        
        return {
            'student_id': student_id,
            'course_id': course_id,
            # Features predictivas (del cuestionario)
            'motivation': motivation,
            'available_time': available_time,
            'sleep_hours': sleep_hours,
            'study_hours': study_hours,
            'enjoyment_studying': enjoyment_studying,
            'study_place_tranquility': study_place_tranquility,
            'academic_pressure': academic_pressure,
            'gender_encoded': gender_encoded,
            # Features transaccionales
            'submission_delay_rate': delay_rate,
            'non_submission_rate': non_submission_rate,
            'average_grade': average_grade,
            'grade_variability': grade_variability
        }
    
    def calculate_target_variable(self, features_df: pd.DataFrame) -> pd.Series:
        """
        Calcula la variable objetivo (Y) basada en las features.
        Riesgo alto (1) si: promedio < 4.0 (en escala 1-7) o tasa de no entrega > 0.5
        
        Si no hay features transaccionales (curso nuevo), usa solo features predictivas:
        - Motivación baja (< 0.3)
        - Presión alta (> 0.7)
        - Tiempo disponible bajo (< 0.3)
        - Horas de sueño bajo (< 0.3)
        """
        # Si hay features transaccionales, usarlas para definir riesgo
        if 'average_grade' in features_df.columns and features_df['average_grade'].notna().any():
            # Desnormalizar average_grade para comparar con 4.0
            average_grade_original = features_df['average_grade'] * 6.0 + 1.0
            
            # Definir riesgo alto basado en datos transaccionales
            risk_high = (
                (average_grade_original < 4.0) | 
                (features_df['non_submission_rate'] > 0.5)
            )
        else:
            # Si no hay datos transaccionales, usar features predictivas
            risk_high = pd.Series([False] * len(features_df), index=features_df.index)
            
            # Aplicar reglas basadas en perfil
            if 'motivation' in features_df.columns:
                risk_high = risk_high | (features_df['motivation'] < 0.3)  # Motivación muy baja
            
            if 'academic_pressure' in features_df.columns:
                risk_high = risk_high | (features_df['academic_pressure'] > 0.7)  # Presión muy alta
            
            if 'available_time' in features_df.columns:
                risk_high = risk_high | (features_df['available_time'] < 0.3)  # Poco tiempo disponible
            
            if 'sleep_hours' in features_df.columns:
                risk_high = risk_high | (features_df['sleep_hours'] < 0.3)  # Poco sueño
        
        return risk_high.astype(int)

