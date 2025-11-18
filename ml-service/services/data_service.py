"""
Servicio para obtener datos de la base de datos
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings


class DataService:
    """Servicio para acceder a los datos de la base de datos"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    
    def get_historical_data(self) -> pd.DataFrame:
        """
        Obtiene todos los datos históricos necesarios para entrenar el modelo.
        Incluye todas las tareas (entregadas y no entregadas) para calcular correctamente
        la tasa de no entrega.
        Retorna un DataFrame con: student_id, course_id, task_id, due_date, 
        submitted_at, grade, etc.
        """
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
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"Error al obtener datos históricos: {e}")
            return pd.DataFrame()
    
    def get_student_course_data(self, student_id: int, course_id: int) -> pd.DataFrame:
        """
        Obtiene los datos de un estudiante específico en un curso específico
        Incluye todas las tareas (entregadas y no entregadas)
        """
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
            WHERE e.student_id = :student_id 
                AND t.course_id = :course_id
            ORDER BY t.due_date
        """)
        
        try:
            df = pd.read_sql(
                query, 
                self.engine,
                params={"student_id": student_id, "course_id": course_id}
            )
            return df
        except Exception as e:
            print(f"Error al obtener datos del estudiante: {e}")
            return pd.DataFrame()
    
    def get_course_students_data(self, course_id: int) -> pd.DataFrame:
        """
        Obtiene los datos de todos los estudiantes en un curso
        Incluye todas las tareas (entregadas y no entregadas)
        """
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
            WHERE t.course_id = :course_id
            ORDER BY e.student_id, t.due_date
        """)
        
        try:
            df = pd.read_sql(
                query,
                self.engine,
                params={"course_id": course_id}
            )
            return df
        except Exception as e:
            print(f"Error al obtener datos del curso: {e}")
            return pd.DataFrame()
    
    def get_all_tasks_for_student_course(self, student_id: int, course_id: int) -> pd.DataFrame:
        """
        Obtiene todas las tareas (entregadas y no entregadas) de un estudiante en un curso
        """
        query = text("""
            SELECT 
                t.id as task_id,
                t.course_id,
                t.due_date,
                t.created_at as task_created_at,
                s.id as submission_id,
                s.submitted_at,
                s.grade,
                e.enrollment_date
            FROM tasks t
            INNER JOIN enrollments e ON t.course_id = e.course_id
            LEFT JOIN submissions s ON s.task_id = t.id AND s.student_id = e.student_id
            WHERE e.student_id = :student_id 
                AND t.course_id = :course_id
            ORDER BY t.due_date
        """)
        
        try:
            df = pd.read_sql(
                query,
                self.engine,
                params={"student_id": student_id, "course_id": course_id}
            )
            return df
        except Exception as e:
            print(f"Error al obtener tareas: {e}")
            return pd.DataFrame()

