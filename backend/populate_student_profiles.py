"""
Script para poblar perfiles de estudiantes históricos basándose en su rendimiento real.
Los perfiles se generan de forma coherente: estudiantes con bajo rendimiento tendrán
perfiles de riesgo alto (baja motivación, alta presión, etc.)
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import numpy as np

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.models.user import User, UserRole
from app.models.student_profile import StudentProfile
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.task import Task

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_student_performance(student_id: int, db: Session) -> dict:
    """
    Calcula el rendimiento de un estudiante basándose en sus entregas y calificaciones.
    Retorna un diccionario con métricas de rendimiento.
    """
    # Obtener todas las inscripciones del estudiante
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    
    if not enrollments:
        return {
            'has_data': False,
            'avg_grade': 0.0,
            'submission_rate': 0.0,
            'late_rate': 0.0
        }
    
    # Obtener todas las tareas de los cursos del estudiante
    course_ids = [e.course_id for e in enrollments]
    tasks = db.query(Task).filter(Task.course_id.in_(course_ids)).all()
    
    if not tasks:
        return {
            'has_data': False,
            'avg_grade': 0.0,
            'submission_rate': 0.0,
            'late_rate': 0.0
        }
    
    # Calcular métricas
    total_tasks = len(tasks)
    submissions = db.query(Submission).filter(
        Submission.student_id == student_id,
        Submission.task_id.in_([t.id for t in tasks])
    ).all()
    
    submitted_count = len(submissions)
    submission_rate = submitted_count / total_tasks if total_tasks > 0 else 0.0
    
    # Calcular promedio de notas
    grades = [s.grade for s in submissions if s.grade is not None]
    avg_grade = sum(grades) / len(grades) if grades else 0.0
    
    # Calcular tasa de retraso
    late_count = 0
    for submission in submissions:
        if submission.submitted_at and submission.task_id:
            task = next((t for t in tasks if t.id == submission.task_id), None)
            if task and task.due_date:
                if submission.submitted_at > task.due_date:
                    late_count += 1
    
    late_rate = late_count / submitted_count if submitted_count > 0 else 0.0
    
    return {
        'has_data': True,
        'avg_grade': avg_grade,
        'submission_rate': submission_rate,
        'late_rate': late_rate,
        'total_tasks': total_tasks,
        'submitted_count': submitted_count
    }


def generate_profile_from_performance(performance: dict) -> dict:
    """
    Genera un perfil de estudiante coherente basándose en su rendimiento real.
    Estudiantes con bajo rendimiento tendrán features de riesgo alto.
    """
    if not performance['has_data']:
        # Si no hay datos, generar un perfil promedio con variación aleatoria
        return {
            'motivation': random.uniform(4.0, 7.0),
            'available_time': random.uniform(4.0, 7.0),
            'sleep_hours': random.uniform(5.0, 8.0),
            'study_hours': random.uniform(4.0, 7.0),
            'enjoyment_studying': random.uniform(4.0, 7.0),
            'study_place_tranquility': random.uniform(5.0, 8.0),
            'academic_pressure': random.uniform(4.0, 7.0),
            'gender': random.choice(['masculino', 'femenino', 'otro'])
        }
    
    avg_grade = performance['avg_grade']
    submission_rate = performance['submission_rate']
    late_rate = performance['late_rate']
    
    # Determinar nivel de riesgo
    # Riesgo alto: promedio < 4.0 o tasa de entrega < 0.5
    is_high_risk = avg_grade < 4.0 or submission_rate < 0.5
    
    # Riesgo medio: promedio 4.0-5.0 o tasa de entrega 0.5-0.7
    is_medium_risk = (4.0 <= avg_grade < 5.0) or (0.5 <= submission_rate < 0.7)
    
    if is_high_risk:
        # Perfil de alto riesgo: baja motivación, alta presión, poco tiempo, etc.
        return {
            'motivation': random.uniform(2.0, 5.0),  # Baja motivación
            'available_time': random.uniform(2.0, 5.0),  # Poco tiempo disponible
            'sleep_hours': random.uniform(2.0, 6.0),  # Poco sueño
            'study_hours': random.uniform(2.0, 5.0),  # Pocas horas de estudio
            'enjoyment_studying': random.uniform(2.0, 5.0),  # No le gusta estudiar
            'study_place_tranquility': random.uniform(3.0, 6.0),  # Lugar poco tranquilo
            'academic_pressure': random.uniform(6.0, 9.0),  # Alta presión
            'gender': random.choice(['masculino', 'femenino', 'otro'])
        }
    elif is_medium_risk:
        # Perfil de riesgo medio: valores intermedios
        return {
            'motivation': random.uniform(4.0, 6.5),  # Motivación media
            'available_time': random.uniform(4.0, 6.5),  # Tiempo medio
            'sleep_hours': random.uniform(5.0, 7.0),  # Sueño medio
            'study_hours': random.uniform(4.0, 6.5),  # Horas de estudio media
            'enjoyment_studying': random.uniform(4.0, 6.5),  # Gusto medio
            'study_place_tranquility': random.uniform(5.0, 7.5),  # Lugar medio tranquilo
            'academic_pressure': random.uniform(5.0, 7.5),  # Presión media-alta
            'gender': random.choice(['masculino', 'femenino', 'otro'])
        }
    else:
        # Perfil de bajo riesgo: alta motivación, buena organización, etc.
        return {
            'motivation': random.uniform(7.0, 10.0),  # Alta motivación
            'available_time': random.uniform(6.0, 9.0),  # Buen tiempo disponible
            'sleep_hours': random.uniform(6.0, 9.0),  # Buen sueño
            'study_hours': random.uniform(6.0, 9.0),  # Buenas horas de estudio
            'enjoyment_studying': random.uniform(6.0, 9.0),  # Le gusta estudiar
            'study_place_tranquility': random.uniform(7.0, 10.0),  # Lugar muy tranquilo
            'academic_pressure': random.uniform(3.0, 6.0),  # Presión manejable
            'gender': random.choice(['masculino', 'femenino', 'otro'])
        }


def populate_profiles(db: Session):
    """Pobla perfiles para todos los estudiantes que no tengan uno"""
    print("=" * 60)
    print("POBLANDO PERFILES DE ESTUDIANTES HISTORICOS")
    print("=" * 60)
    print()
    
    # Obtener todos los estudiantes
    students = db.query(User).filter(User.role == UserRole.ESTUDIANTE).all()
    
    if not students:
        print("No se encontraron estudiantes en la base de datos.")
        return
    
    print(f"Estudiantes encontrados: {len(students)}")
    print()
    
    profiles_created = 0
    profiles_updated = 0
    profiles_skipped = 0
    
    # Semilla para reproducibilidad
    random.seed(42)
    np.random.seed(42)
    
    for i, student in enumerate(students, 1):
        # Verificar si ya tiene perfil
        existing_profile = db.query(StudentProfile).filter(
            StudentProfile.student_id == student.id
        ).first()
        
        if existing_profile:
            # Actualizar perfil existente basándose en rendimiento
            performance = calculate_student_performance(student.id, db)
            profile_data = generate_profile_from_performance(performance)
            
            existing_profile.motivation = profile_data['motivation']
            existing_profile.available_time = profile_data['available_time']
            existing_profile.sleep_hours = profile_data['sleep_hours']
            existing_profile.study_hours = profile_data['study_hours']
            existing_profile.enjoyment_studying = profile_data['enjoyment_studying']
            existing_profile.study_place_tranquility = profile_data['study_place_tranquility']
            existing_profile.academic_pressure = profile_data['academic_pressure']
            existing_profile.gender = profile_data['gender']
            
            db.commit()
            profiles_updated += 1
            
            if i % 50 == 0:
                print(f"  Procesados {i}/{len(students)} estudiantes...")
            continue
        
        # Calcular rendimiento del estudiante
        performance = calculate_student_performance(student.id, db)
        
        # Generar perfil coherente con el rendimiento
        profile_data = generate_profile_from_performance(performance)
        
        # Crear perfil
        profile = StudentProfile(
            student_id=student.id,
            motivation=profile_data['motivation'],
            available_time=profile_data['available_time'],
            sleep_hours=profile_data['sleep_hours'],
            study_hours=profile_data['study_hours'],
            enjoyment_studying=profile_data['enjoyment_studying'],
            study_place_tranquility=profile_data['study_place_tranquility'],
            academic_pressure=profile_data['academic_pressure'],
            gender=profile_data['gender']
        )
        
        db.add(profile)
        profiles_created += 1
        
        # Commit cada 50 estudiantes
        if i % 50 == 0:
            db.commit()
            print(f"  Procesados {i}/{len(students)} estudiantes...")
    
    # Commit final
    db.commit()
    
    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print()
    print(f"Perfiles creados: {profiles_created}")
    print(f"Perfiles actualizados: {profiles_updated}")
    print(f"Total estudiantes procesados: {len(students)}")
    print()
    print("Los perfiles han sido generados de forma coherente con el rendimiento")
    print("de cada estudiante (bajo rendimiento = perfil de riesgo alto).")
    print()


def main():
    """Función principal"""
    db = SessionLocal()
    
    try:
        populate_profiles(db)
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

