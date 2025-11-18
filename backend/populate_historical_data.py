"""
Script para poblar la base de datos con datos históricos simulados.
Esto crea estudiantes, docentes, cursos, tareas, entregas y calificaciones
para poder entrenar el modelo de ML y probar la aplicación.
"""

import sys
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
from app.models.announcement import Announcement
from app.models.comment import Comment
from app.core.security import get_password_hash

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Datos de ejemplo
STUDENT_NAMES = [
    ("Juan", "Pérez", "juan.perez@estudiante.cl"),
    ("María", "González", "maria.gonzalez@estudiante.cl"),
    ("Carlos", "Rodríguez", "carlos.rodriguez@estudiante.cl"),
    ("Ana", "Martínez", "ana.martinez@estudiante.cl"),
    ("Luis", "López", "luis.lopez@estudiante.cl"),
    ("Laura", "Sánchez", "laura.sanchez@estudiante.cl"),
    ("Pedro", "Ramírez", "pedro.ramirez@estudiante.cl"),
    ("Sofía", "Torres", "sofia.torres@estudiante.cl"),
    ("Diego", "Flores", "diego.flores@estudiante.cl"),
    ("Carmen", "Rivera", "carmen.rivera@estudiante.cl"),
    ("Miguel", "Gómez", "miguel.gomez@estudiante.cl"),
    ("Isabel", "Díaz", "isabel.diaz@estudiante.cl"),
    ("Roberto", "Herrera", "roberto.herrera@estudiante.cl"),
    ("Patricia", "Jiménez", "patricia.jimenez@estudiante.cl"),
    ("Fernando", "Morales", "fernando.morales@estudiante.cl"),
    ("Andrea", "Ortiz", "andrea.ortiz@estudiante.cl"),
    ("Javier", "Gutiérrez", "javier.gutierrez@estudiante.cl"),
    ("Natalia", "Castro", "natalia.castro@estudiante.cl"),
    ("Ricardo", "Vargas", "ricardo.vargas@estudiante.cl"),
    ("Valentina", "Ruiz", "valentina.ruiz@estudiante.cl"),
    ("Andrés", "Mendoza", "andres.mendoza@estudiante.cl"),
    ("Daniela", "Silva", "daniela.silva@estudiante.cl"),
    ("Gabriel", "Rojas", "gabriel.rojas@estudiante.cl"),
    ("Camila", "Cruz", "camila.cruz@estudiante.cl"),
    ("Sebastián", "Hernández", "sebastian.hernandez@estudiante.cl"),
]

TEACHER_NAMES = [
    ("Roberto", "Vergara", "roberto.vergara@docente.cl"),
    ("Patricia", "Méndez", "patricia.mendez@docente.cl"),
    ("Carlos", "Fernández", "carlos.fernandez@docente.cl"),
    ("María", "Vega", "maria.vega@docente.cl"),
]

COURSES = [
    {
        "title": "Programación I",
        "description": "Introducción a la programación con Python. Conceptos básicos de algoritmos y estructuras de datos."
    },
    {
        "title": "Base de Datos",
        "description": "Diseño e implementación de bases de datos relacionales. SQL y normalización."
    },
    {
        "title": "Estructuras de Datos",
        "description": "Estudio de estructuras de datos fundamentales: listas, pilas, colas, árboles y grafos."
    },
    {
        "title": "Ingeniería de Software",
        "description": "Metodologías de desarrollo de software, diseño de sistemas y gestión de proyectos."
    },
]

TASK_TEMPLATES = [
    {
        "title": "Tarea 1: Ejercicios Básicos",
        "description": "Resolver los ejercicios del capítulo 1 del libro de texto."
    },
    {
        "title": "Tarea 2: Proyecto Práctico",
        "description": "Desarrollar un proyecto aplicando los conceptos vistos en clase."
    },
    {
        "title": "Tarea 3: Análisis y Diseño",
        "description": "Analizar un problema y diseñar una solución completa."
    },
    {
        "title": "Tarea 4: Implementación",
        "description": "Implementar la solución diseñada en la tarea anterior."
    },
    {
        "title": "Tarea 5: Evaluación Final",
        "description": "Proyecto final que integra todos los conceptos del curso."
    },
]

def create_users(db: Session):
    """Crea usuarios (estudiantes y docentes)"""
    print("Creando usuarios...")
    
    users_created = []
    
    # Crear docentes
    for first_name, last_name, email in TEACHER_NAMES:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            user = User(
                email=email,
                full_name=f"{first_name} {last_name}",
                hashed_password=get_password_hash("password123"),
                role=UserRole.DOCENTE,
                is_active=True
            )
            db.add(user)
            users_created.append(user)
    
    # Crear estudiantes
    for first_name, last_name, email in STUDENT_NAMES:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            user = User(
                email=email,
                full_name=f"{first_name} {last_name}",
                hashed_password=get_password_hash("password123"),
                role=UserRole.ESTUDIANTE,
                is_active=True
            )
            db.add(user)
            users_created.append(user)
    
    db.commit()
    for user in users_created:
        db.refresh(user)
    
    print(f"[OK] Creados {len(users_created)} usuarios")
    return users_created

def create_courses(db: Session, teachers):
    """Crea cursos y los asigna a docentes"""
    print("Creando cursos...")
    
    courses_created = []
    
    for i, course_data in enumerate(COURSES):
        # Asignar docente (rotar entre los docentes)
        teacher = teachers[i % len(teachers)]
        
        course = Course(
            title=course_data["title"],
            description=course_data["description"],
            owner_id=teacher.id,
            created_at=datetime.now(timezone.utc) - timedelta(days=120)  # Curso creado hace 4 meses
        )
        db.add(course)
        courses_created.append(course)
    
    db.commit()
    for course in courses_created:
        db.refresh(course)
    
    print(f"[OK] Creados {len(courses_created)} cursos")
    return courses_created

def enroll_students(db: Session, courses, students):
    """Inscribe estudiantes en cursos"""
    print("Inscribiendo estudiantes en cursos...")
    
    enrollments_created = 0
    
    for course in courses:
        # Inscribir entre 15-20 estudiantes por curso (algunos no se inscriben en todos)
        num_students = random.randint(15, min(20, len(students)))
        selected_students = random.sample(students, num_students)
        
        for student in selected_students:
            existing = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.course_id == course.id
            ).first()
            
            if not existing:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_date=datetime.now(timezone.utc) - timedelta(days=115)  # Inscripción hace ~4 meses
                )
                db.add(enrollment)
                enrollments_created += 1
    
    db.commit()
    print(f"[OK] Creadas {enrollments_created} inscripciones")
    return enrollments_created

def create_tasks(db: Session, courses):
    """Crea tareas para cada curso con fechas pasadas"""
    print("Creando tareas...")
    
    tasks_created = []
    
    for course in courses:
        # Crear 5 tareas por curso, distribuidas a lo largo del semestre
        for i, task_template in enumerate(TASK_TEMPLATES):
            # Fecha límite: distribuir a lo largo de 3 meses
            days_ago = 90 - (i * 20)  # Primera tarea hace 90 días, última hace 10 días
            
            task = Task(
                title=task_template["title"],
                description=task_template["description"],
                due_date=datetime.now(timezone.utc) - timedelta(days=days_ago),
                course_id=course.id,
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago + 7)  # Creada 1 semana antes
            )
            db.add(task)
            tasks_created.append(task)
    
    db.commit()
    for task in tasks_created:
        db.refresh(task)
    
    print(f"[OK] Creadas {len(tasks_created)} tareas")
    return tasks_created

def create_submissions_and_grades(db: Session, tasks, students):
    """Crea entregas y calificaciones con diferentes patrones de comportamiento"""
    print("Creando entregas y calificaciones...")
    
    submissions_created = 0
    grades_assigned = 0
    
    # Agrupar tareas por curso
    tasks_by_course = {}
    for task in tasks:
        if task.course_id not in tasks_by_course:
            tasks_by_course[task.course_id] = []
        tasks_by_course[task.course_id].append(task)
    
    # Obtener enrollments por curso
    enrollments_by_course = {}
    for course_id in tasks_by_course.keys():
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
        enrollments_by_course[course_id] = [e.student_id for e in enrollments]
    
    for course_id, course_tasks in tasks_by_course.items():
        enrolled_students = enrollments_by_course.get(course_id, [])
        
        # Ordenar tareas por fecha (más antigua primero)
        course_tasks.sort(key=lambda t: t.due_date)
        
        for task in course_tasks:
            for student_id in enrolled_students:
                student = next((s for s in students if s.id == student_id), None)
                if not student:
                    continue
                
                # Simular diferentes patrones de comportamiento
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
                        student_id=student_id,
                        task_id=task.id,
                        content=f"Entrega de {task.title} por {student.full_name}",
                        file_path=None,  # Simulamos que no hay archivo
                        submitted_at=submitted_at
                    )
                    db.add(submission)
                    submissions_created += 1
                    db.flush()  # Para obtener el ID
                    
                    # Asignar calificación (simular diferentes niveles de rendimiento)
                    # Patrón: estudiantes con más retrasos y menos entregas tienen peores notas
                    base_score = random.uniform(3.5, 6.5)
                    
                    # Penalizar retrasos
                    if days_late > 0:
                        base_score -= days_late * 0.2
                    
                    # Asegurar que esté en el rango válido
                    grade = max(1.0, min(7.0, round(base_score, 1)))
                    
                    submission.grade = grade
                    submission.feedback = f"Calificación: {grade}/7.0. {'Entrega tardía.' if days_late > 0 else 'Entrega puntual.'}"
                    grades_assigned += 1
    
    db.commit()
    print(f"[OK] Creadas {submissions_created} entregas")
    print(f"[OK] Asignadas {grades_assigned} calificaciones")
    return submissions_created, grades_assigned

def create_announcements(db: Session, courses, teachers):
    """Crea algunos comunicados en los cursos"""
    print("Creando comunicados...")
    
    announcements_created = 0
    
    announcement_templates = [
        {
            "title": "Bienvenida al Curso",
            "content": "Bienvenidos al curso. Les recuerdo revisar el programa y las fechas importantes."
        },
        {
            "title": "Recordatorio: Próxima Tarea",
            "content": "Les recuerdo que la próxima tarea vence el próximo viernes. No olviden entregarla a tiempo."
        },
        {
            "title": "Cambio de Fecha",
            "content": "Se ha cambiado la fecha límite de la tarea 3. Nueva fecha: próxima semana."
        },
        {
            "title": "Resultados de Evaluación",
            "content": "Los resultados de la última evaluación ya están disponibles. Revisen sus calificaciones."
        },
    ]
    
    for course in courses:
        # Crear 2-3 comunicados por curso
        num_announcements = random.randint(2, 3)
        selected_templates = random.sample(announcement_templates, min(num_announcements, len(announcement_templates)))
        
        teacher = next((t for t in teachers if t.id == course.owner_id), None)
        if not teacher:
            continue
        
        for i, template in enumerate(selected_templates):
            days_ago = 100 - (i * 30)  # Distribuir en el tiempo
            
            announcement = Announcement(
                title=template["title"],
                content=template["content"],
                course_id=course.id,
                author_id=teacher.id,
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago)
            )
            db.add(announcement)
            announcements_created += 1
    
    db.commit()
    print(f"[OK] Creados {announcements_created} comunicados")
    return announcements_created

def main():
    """Función principal"""
    print("=" * 60)
    print("POBLADO DE DATOS HISTÓRICOS")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # 1. Crear usuarios
        users = create_users(db)
        teachers = [u for u in users if u.role == UserRole.DOCENTE]
        students = [u for u in users if u.role == UserRole.ESTUDIANTE]
        print()
        
        # 2. Crear cursos
        courses = create_courses(db, teachers)
        print()
        
        # 3. Inscribir estudiantes
        enroll_students(db, courses, students)
        print()
        
        # 4. Crear tareas
        tasks = create_tasks(db, courses)
        print()
        
        # 5. Crear entregas y calificaciones
        create_submissions_and_grades(db, tasks, students)
        print()
        
        # 6. Crear comunicados
        create_announcements(db, courses, teachers)
        print()
        
        print("=" * 60)
        print("[OK] POBLADO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print()
        print("Resumen:")
        print(f"  - Usuarios: {len(users)} ({len(teachers)} docentes, {len(students)} estudiantes)")
        print(f"  - Cursos: {len(courses)}")
        print(f"  - Tareas: {len(tasks)}")
        print()
        print("Credenciales de acceso:")
        print("  Docentes: email del docente / password123")
        print("  Estudiantes: email del estudiante / password123")
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

