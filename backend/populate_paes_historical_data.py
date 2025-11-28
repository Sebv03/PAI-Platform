# backend/populate_paes_historical_data.py
"""
Script para poblar la plataforma PAES con datos históricos de estudiantes de 1° a 4° medio (14-18 años).
Incluye estudiantes, inscripciones, tareas, entregas, calificaciones y perfiles de estudiantes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

from app.core.config import settings
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.task import Task
from app.models.submission import Submission
from app.models.student_profile import StudentProfile
from app.core.security import get_password_hash

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Niveles de enseñanza media y edades correspondientes
GRADE_LEVELS = ["1° medio", "2° medio", "3° medio", "4° medio"]
GRADE_AGE_MAP = {
    "1° medio": (14, 15),
    "2° medio": (15, 16),
    "3° medio": (16, 17),
    "4° medio": (17, 18)
}

# Nombres de estudiantes chilenos (comunes)
FIRST_NAMES = [
    "Juan", "María", "Carlos", "Ana", "Luis", "Laura", "Pedro", "Sofía", "Diego", "Carmen",
    "Miguel", "Isabel", "Roberto", "Patricia", "Fernando", "Andrea", "Javier", "Natalia", "Ricardo", "Gabriela",
    "Daniel", "María José", "Andrés", "Francisca", "Sebastián", "Valentina", "Matías", "Constanza", "Felipe", "Javiera",
    "Nicolás", "Catalina", "Ignacio", "Fernanda", "Pablo", "Isidora", "Martín", "Antonia", "Tomás", "Trinidad",
    "Maximiliano", "Amanda", "Benjamin", "Agustina", "Cristóbal", "Rocío", "Vicente", "Macarena", "Rodrigo", "Pía",
    "Gonzalo", "Vicenta", "Esteban", "Daniela", "Francisco", "Camila", "José", "Paz", "Simón", "Magdalena"
]

LAST_NAMES = [
    "Pérez", "González", "Rodríguez", "Martínez", "López", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera",
    "Gómez", "Díaz", "Herrera", "Jiménez", "Morales", "Ortiz", "Gutiérrez", "Castro", "Vargas", "Ramos",
    "Medina", "Ruiz", "Soto", "Silva", "Hernández", "Mendoza", "Chávez", "Navarro", "Cruz", "Delgado",
    "Peña", "Cortés", "Rojas", "Vega", "Guerrero", "Muñoz", "Ortega", "Salinas", "Vásquez", "Campos"
]

GENDERS = ["Masculino", "Femenino"]

def generate_student_name(index):
    """Genera un nombre único para un estudiante"""
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
    return f"{first} {last}"

def generate_student_email(index):
    """Genera un email único para un estudiante"""
    first = FIRST_NAMES[index % len(FIRST_NAMES)].lower()
    last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)].lower()
    return f"{first}.{last}.{index}@estudiante.pai.cl"

def generate_grade_level_and_age():
    """Genera un nivel y edad aleatorios pero coherentes"""
    grade_level = random.choice(GRADE_LEVELS)
    min_age, max_age = GRADE_AGE_MAP[grade_level]
    age = random.randint(min_age, max_age)
    return grade_level, age

def generate_student_profile(student_id, grade_level, age, performance_level="average"):
    """
    Genera un perfil de estudiante coherente con su nivel de desempeño esperado.
    performance_level: "high", "average", "low"
    """
    if performance_level == "high":
        # Estudiantes de alto rendimiento: alta motivación, buen ambiente, etc.
        motivation = random.uniform(7.0, 9.5)
        available_time = random.uniform(6.0, 9.0)
        sleep_hours = random.uniform(6.0, 8.5)
        study_hours = random.uniform(7.0, 9.5)
        enjoyment_studying = random.uniform(7.0, 9.5)
        study_place_tranquility = random.uniform(7.0, 9.5)
        academic_pressure = random.uniform(4.0, 7.0)  # Presión moderada
    elif performance_level == "low":
        # Estudiantes de bajo rendimiento: baja motivación, poco tiempo, etc.
        motivation = random.uniform(2.0, 5.0)
        available_time = random.uniform(2.0, 5.0)
        sleep_hours = random.uniform(4.0, 6.5)
        study_hours = random.uniform(2.0, 5.0)
        enjoyment_studying = random.uniform(2.0, 5.0)
        study_place_tranquility = random.uniform(3.0, 6.0)
        academic_pressure = random.uniform(6.0, 9.5)  # Alta presión
    else:
        # Rendimiento promedio
        motivation = random.uniform(4.5, 7.5)
        available_time = random.uniform(4.0, 7.0)
        sleep_hours = random.uniform(5.0, 7.5)
        study_hours = random.uniform(4.0, 7.5)
        enjoyment_studying = random.uniform(4.0, 7.5)
        study_place_tranquility = random.uniform(4.5, 7.5)
        academic_pressure = random.uniform(4.5, 7.5)
    
    gender = random.choice(GENDERS)
    
    return {
        "student_id": student_id,
        "motivation": round(motivation, 1),
        "available_time": round(available_time, 1),
        "sleep_hours": round(sleep_hours, 1),
        "study_hours": round(study_hours, 1),
        "enjoyment_studying": round(enjoyment_studying, 1),
        "study_place_tranquility": round(study_place_tranquility, 1),
        "academic_pressure": round(academic_pressure, 1),
        "gender": gender,
        "grade_level": grade_level,
        "age": age
    }

def calculate_grade_based_on_profile(profile_data):
    """Calcula una nota (1.0-7.0) basada en el perfil del estudiante"""
    # Nota base del perfil
    base_score = (
        profile_data["motivation"] * 0.2 +
        profile_data["available_time"] * 0.1 +
        profile_data["sleep_hours"] * 0.1 +
        profile_data["study_hours"] * 0.2 +
        profile_data["enjoyment_studying"] * 0.15 +
        profile_data["study_place_tranquility"] * 0.1 -
        profile_data["academic_pressure"] * 0.05  # Presión alta baja la nota
    ) / 10.0  # Normalizar a 0-1
    
    # Convertir a escala 1.0-7.0
    grade = 1.0 + (base_score * 6.0)
    
    # Agregar algo de variabilidad
    grade += random.uniform(-0.5, 0.5)
    
    # Asegurar que esté en el rango 1.0-7.0
    grade = max(1.0, min(7.0, grade))
    
    return round(grade, 1)

def create_students(db: Session, num_students=200):
    """Crea estudiantes de 1° a 4° medio"""
    print(f"Creando {num_students} estudiantes...")
    
    students = []
    profiles = []
    
    for i in range(num_students):
        grade_level, age = generate_grade_level_and_age()
        
        # Distribuir niveles de desempeño: 30% alto, 40% promedio, 30% bajo
        rand = random.random()
        if rand < 0.3:
            performance = "high"
        elif rand < 0.7:
            performance = "average"
        else:
            performance = "low"
        
        # Crear estudiante
        student = User(
            email=generate_student_email(i),
            full_name=generate_student_name(i),
            hashed_password=get_password_hash("estudiante123"),
            role=UserRole.ESTUDIANTE,
            is_active=True
        )
        db.add(student)
        db.flush()  # Para obtener el ID
        
        students.append(student)
        
        # Crear perfil
        profile_data = generate_student_profile(student.id, grade_level, age, performance)
        profile = StudentProfile(**profile_data)
        db.add(profile)
        profiles.append(profile)
        
        if (i + 1) % 50 == 0:
            print(f"  Creados {i + 1} estudiantes...")
    
    db.commit()
    print(f"[OK] Creados {len(students)} estudiantes con sus perfiles")
    return students, profiles

def enroll_students_in_courses(db: Session, courses, students):
    """Inscribe estudiantes en cursos (cada estudiante en varios cursos)"""
    print("Inscribiendo estudiantes en cursos...")
    
    enrollments = []
    
    for student in students:
        # Cada estudiante se inscribe en 3-6 cursos aleatorios
        num_courses = random.randint(3, 6)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id,
                enrollment_date=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 180))
            )
            db.add(enrollment)
            enrollments.append(enrollment)
    
    db.commit()
    print(f"[OK] Creadas {len(enrollments)} inscripciones")
    return enrollments

def create_tasks_for_courses(db: Session, courses):
    """Crea tareas para cada curso"""
    print("Creando tareas para los cursos...")
    
    tasks = []
    
    for course in courses:
        # Cada curso tiene 5-8 tareas
        num_tasks = random.randint(5, 8)
        
        for i in range(num_tasks):
            # Fechas distribuidas en los últimos 4 meses
            created_days_ago = random.randint(10, 120)
            due_days_ago = random.randint(0, created_days_ago - 1)
            
            task = Task(
                title=f"Tarea {i + 1} - {course.title}",
                description=f"Tarea de práctica PAES sobre {course.paes_topic or 'el tema del curso'}",
                course_id=course.id,
                due_date=datetime.now(timezone.utc) - timedelta(days=due_days_ago),
                created_at=datetime.now(timezone.utc) - timedelta(days=created_days_ago)
            )
            db.add(task)
            tasks.append(task)
    
    db.commit()
    print(f"[OK] Creadas {len(tasks)} tareas")
    return tasks

def create_submissions_and_grades(db: Session, tasks, students, profiles_map):
    """Crea entregas y calificaciones coherentes con el perfil del estudiante"""
    print("Creando entregas y calificaciones...")
    
    submissions = []
    submission_count = 0
    
    for task in tasks:
        # Obtener estudiantes inscritos en el curso de esta tarea
        enrolled_students = db.query(User).join(Enrollment).filter(
            Enrollment.course_id == task.course_id,
            User.role == UserRole.ESTUDIANTE
        ).all()
        
        for student in enrolled_students:
            # Obtener perfil del estudiante
            profile = profiles_map.get(student.id)
            if not profile:
                continue
            
            # Decidir si entrega o no (basado en motivación y disponibilidad)
            submission_probability = (profile.motivation + profile.available_time) / 20.0
            submission_probability = min(0.95, max(0.3, submission_probability))  # Entre 30% y 95%
            
            will_submit = random.random() < submission_probability
            
            if will_submit:
                # Calcular nota basada en el perfil
                grade = calculate_grade_based_on_profile({
                    "motivation": profile.motivation,
                    "available_time": profile.available_time,
                    "sleep_hours": profile.sleep_hours,
                    "study_hours": profile.study_hours,
                    "enjoyment_studying": profile.enjoyment_studying,
                    "study_place_tranquility": profile.study_place_tranquility,
                    "academic_pressure": profile.academic_pressure
                })
                
                # Fecha de entrega (puede ser antes o después de la fecha límite)
                days_late = 0
                if random.random() < 0.3:  # 30% entregan tarde
                    days_late = random.randint(1, 5)
                
                submitted_at = task.due_date + timedelta(days=days_late)
                
                submission = Submission(
                    student_id=student.id,
                    task_id=task.id,
                    submitted_at=submitted_at,
                    grade=grade
                )
                db.add(submission)
                submissions.append(submission)
                submission_count += 1
    
    db.commit()
    print(f"[OK] Creadas {submission_count} entregas con calificaciones")
    return submissions

def main():
    """Función principal"""
    print("=" * 70)
    print("POBLADO DE DATOS HISTORICOS PAES - Plataforma Preuniversitaria")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    
    try:
        # 1. Obtener cursos existentes
        courses = db.query(Course).all()
        if not courses:
            print("[ERROR] No hay cursos en la plataforma. Ejecuta primero setup_paes_structure.py")
            return
        
        print(f"Encontrados {len(courses)} cursos")
        
        # 2. Crear estudiantes con perfiles
        students, profiles = create_students(db, num_students=200)
        print()
        
        # 3. Crear mapa de perfiles para acceso rápido
        profiles_map = {p.student_id: p for p in profiles}
        
        # 4. Inscribir estudiantes en cursos
        enroll_students_in_courses(db, courses, students)
        print()
        
        # 5. Crear tareas
        tasks = create_tasks_for_courses(db, courses)
        print()
        
        # 6. Crear entregas y calificaciones
        create_submissions_and_grades(db, tasks, students, profiles_map)
        print()
        
        # 7. Obtener profesor de matemáticas
        math_professor = db.query(User).filter(
            User.email == "profesor.matematicas@pai.cl"
        ).first()
        
        # 8. Seleccionar un estudiante de ejemplo
        example_student = students[0] if students else None
        
        print("=" * 70)
        print("[OK] POBLADO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print()
        print("Resumen:")
        print(f"  - Estudiantes creados: {len(students)}")
        print(f"  - Perfiles de estudiantes: {len(profiles)}")
        print(f"  - Cursos: {len(courses)}")
        print(f"  - Tareas creadas: {len(tasks)}")
        print()
        print("=" * 70)
        print("CREDENCIALES DE ACCESO")
        print("=" * 70)
        print()
        
        if math_professor:
            print("PROFESOR MATEMATICAS:")
            print(f"  Email: {math_professor.email}")
            print(f"  Password: profesor123")
            print(f"  Nombre: {math_professor.full_name}")
            print()
        
        if example_student:
            print("ESTUDIANTE DE EJEMPLO:")
            print(f"  Email: {example_student.email}")
            print(f"  Password: estudiante123")
            print(f"  Nombre: {example_student.full_name}")
            profile = profiles_map.get(example_student.id)
            if profile:
                print(f"  Nivel: {profile.grade_level}")
                print(f"  Edad: {profile.age} años")
            print()
        
        print("NOTA: Todos los estudiantes tienen la misma contraseña: estudiante123")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error durante el poblado: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()





