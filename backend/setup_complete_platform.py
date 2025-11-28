"""
Script maestro para configurar la plataforma PAI completa desde cero.
Este script ejecuta todos los pasos necesarios en el orden correcto:
1. Crear tablas de base de datos
2. Crear usuario administrador
3. Configurar estructura PAES (profesores y cursos)
4. Poblar datos históricos (estudiantes, inscripciones, tareas, entregas)

IMPORTANTE: Este script usa seeds fijos para generar siempre los mismos datos.

Uso:
    python setup_complete_platform.py

Este script puede ejecutarse múltiples veces. Si detecta datos existentes, 
los eliminará y recreará todo desde cero.
"""

import sys
from pathlib import Path

# Agregar el directorio al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

import random
from sqlalchemy import inspect
from app.db.session import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.task import Task
from app.models.submission import Submission
from app.models.student_profile import StudentProfile
from app.core.security import get_password_hash
from app.main import create_tables

# Importar funciones de otros scripts
from setup_paes_structure import (
    delete_all_data,
    create_professors_and_courses,
    PAES_STRUCTURE
)
from populate_paes_historical_data import (
    create_students,
    enroll_students_in_courses,
    create_tasks_for_courses,
    create_submissions_and_grades
)

def setup_complete_platform():
    """Función principal que ejecuta todo el setup"""
    
    print("=" * 70)
    print("CONFIGURACION COMPLETA DE PLATAFORMA PAI")
    print("Plataforma Preuniversitaria - Setup Completo")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    
    try:
        # ============================================
        # PASO 1: Crear tablas si no existen
        # ============================================
        print("[PASO 1/5] Verificando estructura de base de datos...")
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            print("  Creando tablas...")
            create_tables()
            print("  [OK] Tablas creadas")
        else:
            print(f"  [OK] Base de datos ya tiene {len(existing_tables)} tablas")
        
        print()
        
        # ============================================
        # PASO 2: Crear usuario administrador
        # ============================================
        print("[PASO 2/5] Creando usuario administrador...")
        
        admin_email = "admin@pai.cl"
        admin_password = "admin123"
        admin_name = "Administrador"
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            if existing_admin.role == UserRole.ADMINISTRADOR:
                print(f"  [OK] Administrador ya existe: {admin_email}")
            else:
                existing_admin.role = UserRole.ADMINISTRADOR
                existing_admin.hashed_password = get_password_hash(admin_password)
                db.commit()
                print(f"  [OK] Usuario actualizado a administrador: {admin_email}")
        else:
            admin_user = User(
                email=admin_email,
                full_name=admin_name,
                hashed_password=get_password_hash(admin_password),
                role=UserRole.ADMINISTRADOR,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"  [OK] Administrador creado: {admin_email}")
        
        print()
        
        # ============================================
        # PASO 3: Configurar estructura PAES
        # (Profesores y cursos)
        # ============================================
        print("[PASO 3/5] Configurando estructura PAES...")
        print("  (Profesores y cursos)")
        
        # Verificar si ya existen profesores o cursos
        existing_professors = 0
        existing_courses = 0
        
        try:
            existing_professors = db.query(User).filter(User.role == UserRole.DOCENTE).count()
            existing_courses = db.query(Course).count()
        except (AttributeError, TypeError):
            # Si las tablas no existen, no hay datos previos
            existing_professors = 0
            existing_courses = 0
        
        if existing_professors > 0 or existing_courses > 0:
            print("  Eliminando datos existentes...")
            delete_all_data(db)
            print("  [OK] Datos eliminados")
        
        professors, courses = create_professors_and_courses(db)
        print(f"  [OK] Estructura PAES configurada:")
        print(f"       - {len(professors)} profesores")
        print(f"       - {len(courses)} cursos")
        
        print()
        
        # ============================================
        # PASO 4: Poblar datos históricos
        # (Estudiantes, inscripciones, tareas)
        # ============================================
        print("[PASO 4/5] Poblando datos históricos...")
        print("  (Estudiantes, inscripciones, tareas, entregas)")
        
        # Usar seed fijo para reproducibilidad
        SEED = 42
        random.seed(SEED)
        print(f"  Usando seed: {SEED} (para datos reproducibles)")
        
        # Obtener cursos creados
        courses = db.query(Course).all()
        if not courses:
            print("  [ERROR] No hay cursos. Verifica el paso anterior.")
            return
        
        # Crear estudiantes
        students, _ = create_students(db, num_students=200)
        print(f"  [OK] {len(students)} estudiantes creados")
        
        # Crear mapa de perfiles (necesario para crear entregas)
        profiles_map = {}
        for profile in db.query(StudentProfile).all():
            profiles_map[profile.student_id] = profile
        
        # Inscribir estudiantes
        enrollments_count_before = db.query(Enrollment).count()
        enroll_students_in_courses(db, courses, students)
        db.commit()  # Asegurar que las inscripciones se guarden
        enrollments_count_after = db.query(Enrollment).count()
        print(f"  [OK] {enrollments_count_after - enrollments_count_before} inscripciones creadas")
        
        # Crear tareas
        tasks = create_tasks_for_courses(db, courses)
        db.commit()  # Asegurar que las tareas se guarden
        print(f"  [OK] {len(tasks)} tareas creadas")
        
        # Crear entregas y calificaciones
        submissions_count_before = db.query(Submission).count()
        create_submissions_and_grades(db, tasks, students, profiles_map)
        db.commit()  # Asegurar que las entregas se guarden
        submissions_count_after = db.query(Submission).count()
        print(f"  [OK] {submissions_count_after - submissions_count_before} entregas con calificaciones creadas")
        
        print()
        
        # ============================================
        # PASO 5: Resumen final
        # ============================================
        print("[PASO 5/5] Generando resumen...")
        
        # Obtener conteos finales
        db.commit()  # Asegurar que todos los cambios estén guardados
        final_stats = {
            "administradores": db.query(User).filter(User.role == UserRole.ADMINISTRADOR).count(),
            "profesores": db.query(User).filter(User.role == UserRole.DOCENTE).count(),
            "estudiantes": db.query(User).filter(User.role == UserRole.ESTUDIANTE).count(),
            "cursos": db.query(Course).count(),
            "inscripciones": db.query(Enrollment).count(),
            "tareas": db.query(Task).count(),
            "entregas": db.query(Submission).count(),
            "perfiles": db.query(StudentProfile).count()
        }
        
        print()
        print("=" * 70)
        print("✅ CONFIGURACION COMPLETA EXITOSA")
        print("=" * 70)
        print()
        print("📊 RESUMEN DE DATOS:")
        print(f"   👨‍💼 Administradores: {final_stats['administradores']}")
        print(f"   👨‍🏫 Profesores: {final_stats['profesores']}")
        print(f"   👨‍🎓 Estudiantes: {final_stats['estudiantes']}")
        print(f"   📚 Cursos: {final_stats['cursos']}")
        print(f"   📝 Inscripciones: {final_stats['inscripciones']}")
        print(f"   ✅ Tareas: {final_stats['tareas']}")
        print(f"   📄 Entregas: {final_stats['entregas']}")
        print(f"   👤 Perfiles de estudiantes: {final_stats['perfiles']}")
        print()
        print("=" * 70)
        print("🔐 CREDENCIALES DE ACCESO")
        print("=" * 70)
        print()
        print("ADMINISTRADOR:")
        print("   Email: admin@pai.cl")
        print("   Password: admin123")
        print()
        print("PROFESORES:")
        for config in PAES_STRUCTURE.values():
            print(f"   {config['professor_name']}:")
            print(f"      Email: {config['professor_email']}")
            print("      Password: profesor123")
        print()
        print("ESTUDIANTES:")
        if students:
            example_student = students[0]
            print(f"   Ejemplo: {example_student.full_name}")
            print(f"      Email: {example_student.email}")
            print(f"      Password: estudiante123")
            print(f"   NOTA: Todos los {len(students)} estudiantes tienen la misma contraseña")
        print()
        print("=" * 70)
        print("🚀 PRÓXIMOS PASOS")
        print("=" * 70)
        print()
        print("1. Iniciar los servicios:")
        print("   - Backend: uvicorn app.main:app --reload --port 8000")
        print("   - Frontend: npm run dev (en directorio frontend/)")
        print("   - ML Service: python main.py (en directorio ml-service/)")
        print()
        print("2. Acceder a la plataforma:")
        print("   - Frontend: http://localhost:5173")
        print("   - Backend API: http://localhost:8000/docs")
        print("   - ML Service: http://localhost:8001/health")
        print()
        print("3. Entrenar el modelo ML:")
        print("   - Inicia sesion como administrador")
        print("   - Ve al Admin Dashboard")
        print("   - Haz clic en 'Entrenar Modelo ML'")
        print()
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 70)
        print("❌ ERROR DURANTE LA CONFIGURACION")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    setup_complete_platform()

