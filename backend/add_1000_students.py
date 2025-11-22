"""
Script para agregar 1000 estudiantes adicionales al dataset histórico
Genera estudiantes con nombres y emails únicos, los inscribe en cursos
y crea entregas y calificaciones para ellos.

USO:
    cd backend
    venv\Scripts\activate  # En Windows (o source venv/bin/activate en Linux)
    python add_1000_students.py
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

# Importar modelos y funciones CRUD
from app.core.config import settings
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.task import Task
from app.models.submission import Submission
from app.core.security import get_password_hash

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Nombres comunes para generar estudiantes
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
    
    # Agregar número para hacer único si es necesario
    if index > 0:
        # Combinar nombres con variaciones
        middle_part = random.choice(["", f"{random.randint(1, 99)}", "", ""])
        if middle_part:
            full_name = f"{first_name} {middle_part} {last_name}"
        else:
            full_name = f"{first_name} {last_name}"
    else:
        full_name = f"{first_name} {last_name}"
    
    # Generar email único
    base_email = f"{first_name.lower()}.{last_name.lower()}"
    email = f"{base_email}{index}@estudiante.cl"
    
    return first_name, last_name, full_name, email


def create_additional_students(db: Session, num_students=1000):
    """Crea estudiantes adicionales"""
    print(f"Creando {num_students} estudiantes adicionales...")
    
    students_created = []
    
    # Obtener el siguiente número para emails únicos
    existing_count = db.query(User).filter(User.role == UserRole.ESTUDIANTE).count()
    start_index = existing_count + 1
    
    batch_size = 100  # Procesar en lotes para mejor rendimiento
    
    for batch_start in range(0, num_students, batch_size):
        batch_end = min(batch_start + batch_size, num_students)
        batch_students = []
        
        for i in range(batch_start, batch_end):
            index = start_index + i
            first_name, last_name, full_name, email = generate_student_name(index)
            
            # Verificar que el email no exista
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                # Si existe, generar variación
                email = f"{first_name.lower()}.{last_name.lower()}{index}{random.randint(100, 999)}@estudiante.cl"
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    continue  # Saltar si todavía existe
            
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash("password123"),
                role=UserRole.ESTUDIANTE,
                is_active=True,
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(90, 120))
            )
            db.add(user)
            batch_students.append(user)
        
        db.flush()  # Flush pero no commit todavía
        
        for student in batch_students:
            db.refresh(student)
        
        students_created.extend(batch_students)
        
        if (batch_start // batch_size + 1) % 10 == 0:
            print(f"  Procesados {batch_end}/{num_students} estudiantes...")
    
    db.commit()
    
    print(f"[OK] Creados {len(students_created)} estudiantes adicionales")
    return students_created


def enroll_additional_students(db: Session, students, courses):
    """Inscribe estudiantes adicionales en cursos"""
    print("Inscribiendo estudiantes adicionales en cursos...")
    
    enrollments_created = 0
    
    for student in students:
        # Cada estudiante se inscribe en 1-3 cursos aleatorios
        num_courses = random.randint(1, 3)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            # Verificar que no esté ya inscrito
            existing = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.course_id == course.id
            ).first()
            
            if not existing:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_date=datetime.now(timezone.utc) - timedelta(days=random.randint(85, 115))
                )
                db.add(enrollment)
                enrollments_created += 1
        
        # Commit cada 50 inscripciones para mejor rendimiento
        if enrollments_created % 50 == 0:
            db.commit()
    
    db.commit()
    print(f"[OK] Creadas {enrollments_created} inscripciones adicionales")
    return enrollments_created


def create_additional_submissions(db: Session, students, courses):
    """Crea entregas y calificaciones para estudiantes adicionales"""
    print("Creando entregas y calificaciones para estudiantes adicionales...")
    
    # Obtener todas las tareas de los cursos
    all_tasks = db.query(Task).filter(Task.course_id.in_([c.id for c in courses])).all()
    
    # Agrupar tareas por curso
    tasks_by_course = {}
    for task in all_tasks:
        if task.course_id not in tasks_by_course:
            tasks_by_course[task.course_id] = []
        tasks_by_course[task.course_id].append(task)
    
    # Obtener inscripciones por estudiante
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id.in_([s.id for s in students])
    ).all()
    
    enrollments_by_student = {}
    for enrollment in enrollments:
        if enrollment.student_id not in enrollments_by_student:
            enrollments_by_student[enrollment.student_id] = []
        enrollments_by_student[enrollment.student_id].append(enrollment.course_id)
    
    submissions_created = 0
    grades_assigned = 0
    
    # Procesar en lotes
    batch_size = 50
    for batch_start in range(0, len(students), batch_size):
        batch_end = min(batch_start + batch_size, len(students))
        batch_students = students[batch_start:batch_end]
        
        for student in batch_students:
            student_courses = enrollments_by_student.get(student.id, [])
            
            for course_id in student_courses:
                course_tasks = tasks_by_course.get(course_id, [])
                
                for task in course_tasks:
                    # 70% de probabilidad de entregar (30% no entrega)
                    will_submit = random.random() < 0.70
                    
                    if will_submit:
                        # Determinar si entrega a tiempo o con retraso
                        days_late = 0
                        if random.random() < 0.35:  # 35% entrega con retraso
                            days_late = random.randint(1, 7)
                        
                        submitted_at = task.due_date + timedelta(days=days_late)
                        
                        # Crear submission
                        submission = Submission(
                            student_id=student.id,
                            task_id=task.id,
                            content=f"Entrega de {task.title} por {student.full_name}",
                            file_path=None,
                            submitted_at=submitted_at
                        )
                        db.add(submission)
                        submissions_created += 1
                        db.flush()  # Para obtener el ID
                        
                        # Asignar calificación
                        # Simular diferentes niveles de rendimiento
                        base_score = random.uniform(3.5, 6.5)
                        
                        # Penalizar retrasos
                        if days_late > 0:
                            base_score -= days_late * 0.2
                        
                        # Asegurar que esté en el rango válido
                        grade = max(1.0, min(7.0, round(base_score, 1)))
                        
                        submission.grade = grade
                        submission.feedback = f"Calificación: {grade}/7.0. {'Entrega tardía.' if days_late > 0 else 'Entrega puntual.'}"
                        grades_assigned += 1
        
        # Commit cada batch
        if (batch_start // batch_size + 1) % 10 == 0:
            print(f"  Procesados {batch_end}/{len(students)} estudiantes...")
            db.commit()
    
    db.commit()
    print(f"[OK] Creadas {submissions_created} entregas adicionales")
    print(f"[OK] Asignadas {grades_assigned} calificaciones adicionales")
    return submissions_created, grades_assigned


def main():
    """Función principal"""
    print("=" * 60)
    print("AGREGAR 1000 ESTUDIANTES AL DATASET HISTÓRICO")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # 1. Obtener cursos existentes
        courses = db.query(Course).all()
        if not courses:
            print("ERROR: No hay cursos en la base de datos.")
            print("Por favor, ejecuta primero populate_historical_data.py")
            return
        
        print(f"Cursos encontrados: {len(courses)}")
        print()
        
        # 2. Crear estudiantes adicionales
        students = create_additional_students(db, num_students=1000)
        print()
        
        if not students:
            print("ERROR: No se pudieron crear estudiantes.")
            return
        
        # 3. Inscribir estudiantes en cursos
        enrollments = enroll_additional_students(db, students, courses)
        print()
        
        # 4. Crear entregas y calificaciones
        submissions, grades = create_additional_submissions(db, students, courses)
        print()
        
        print("=" * 60)
        print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print()
        print("Resumen:")
        print(f"  - Estudiantes adicionales: {len(students)}")
        print(f"  - Inscripciones creadas: {enrollments}")
        print(f"  - Entregas creadas: {submissions}")
        print(f"  - Calificaciones asignadas: {grades}")
        print()
        print("Ahora puedes exportar el dataset actualizado ejecutando:")
        print("  python export_historical_data_to_csv.py")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

