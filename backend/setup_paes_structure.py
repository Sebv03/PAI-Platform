# backend/setup_paes_structure.py
"""
Script para configurar la estructura base de la plataforma PAES
- Borra todos los datos existentes
- Crea profesores de cada asignatura
- Crea cursos específicos para preparación PAES
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.task import Task
from app.models.submission import Submission
from app.models.announcement import Announcement
from app.models.comment import Comment
from app.models.student_profile import StudentProfile
from app.core.security import get_password_hash

# Configuración de profesores y cursos PAES
PAES_STRUCTURE = {
    "Matemáticas": {
        "professor_email": "profesor.matematicas@pai.cl",
        "professor_name": "Profesor Matemáticas",
        "courses": [
            {
                "title": "Números",
                "description": "Conjuntos numéricos, operaciones, porcentajes, potencias, raíces, logaritmos.",
                "subject": "Matemáticas",
                "paes_topic": "Números"
            },
            {
                "title": "Álgebra y Funciones",
                "description": "Expresiones algebraicas, ecuaciones lineales y cuadráticas, sistemas de ecuaciones, funciones (lineal, afín, cuadrática, exponencial).",
                "subject": "Matemáticas",
                "paes_topic": "Álgebra y Funciones"
            },
            {
                "title": "Geometría",
                "description": "Figuras 2D y 3D, transformaciones isométricas, semejanza, teorema de Thales, vectores, recta en el plano.",
                "subject": "Matemáticas",
                "paes_topic": "Geometría"
            },
            {
                "title": "Probabilidad y Estadística",
                "description": "Tablas y gráficos, medidas de tendencia central (media, mediana, moda), medidas de posición (percentiles), reglas de probabilidad, combinatoria básica.",
                "subject": "Matemáticas",
                "paes_topic": "Probabilidad y Estadística"
            }
        ]
    },
    "Lenguaje": {
        "professor_email": "profesor.lenguaje@pai.cl",
        "professor_name": "Profesor Lenguaje",
        "courses": [
            {
                "title": "Estrategias de Comprensión Lectora",
                "description": "Curso base sobre técnicas de lectura activa, identificación de ideas principales, etc.",
                "subject": "Lenguaje",
                "paes_topic": "Comprensión Lectora"
            },
            {
                "title": "Localizar Información",
                "description": "Ejercicios enfocados en extraer información explícita del texto.",
                "subject": "Lenguaje",
                "paes_topic": "Localizar Información"
            },
            {
                "title": "Interpretar y Relacionar",
                "description": "Ejercicios para hacer inferencias, establecer relaciones entre partes del texto, sintetizar.",
                "subject": "Lenguaje",
                "paes_topic": "Interpretar y Relacionar"
            },
            {
                "title": "Evaluar y Reflexionar",
                "description": "Ejercicios para juzgar críticamente el contenido, propósito o forma del texto.",
                "subject": "Lenguaje",
                "paes_topic": "Evaluar y Reflexionar"
            },
            {
                "title": "Tipos de Texto",
                "description": "Módulos específicos para textos literarios (narrativos, dramáticos) y no literarios (informativos, argumentativos, medios masivos).",
                "subject": "Lenguaje",
                "paes_topic": "Tipos de Texto"
            }
        ]
    },
    "Ciencias": {
        "professor_email": "profesor.ciencias@pai.cl",
        "professor_name": "Profesor Ciencias",
        "courses": [
            {
                "title": "Biología",
                "description": "Célula, organismo y ambiente, herencia y evolución.",
                "subject": "Ciencias",
                "paes_topic": "Biología"
            },
            {
                "title": "Física",
                "description": "Ondas, mecánica (movimiento y fuerza), energía, electricidad.",
                "subject": "Ciencias",
                "paes_topic": "Física"
            },
            {
                "title": "Química",
                "description": "Estructura atómica, enlace químico, reacciones químicas, estequiometría, química orgánica básica.",
                "subject": "Ciencias",
                "paes_topic": "Química"
            }
        ]
    },
    "Historia": {
        "professor_email": "profesor.historia@pai.cl",
        "professor_name": "Profesor Historia",
        "courses": [
            {
                "title": "Historia en perspectiva: Mundo, América y Chile",
                "description": "Procesos históricos clave desde el siglo XIX hasta la actualidad (guerras mundiales, Guerra Fría, historia de Chile reciente).",
                "subject": "Historia",
                "paes_topic": "Historia en perspectiva"
            },
            {
                "title": "Formación Ciudadana",
                "description": "Estado, democracia, derechos humanos, participación ciudadana, institucionalidad en Chile.",
                "subject": "Historia",
                "paes_topic": "Formación Ciudadana"
            },
            {
                "title": "Economía y Sociedad",
                "description": "Conceptos básicos de economía, sistema económico nacional, problemas económicos actuales, desarrollo sustentable.",
                "subject": "Historia",
                "paes_topic": "Economía y Sociedad"
            }
        ]
    }
}

def delete_all_data(db):
    """Borra todos los datos de las tablas en orden correcto (respetando foreign keys)"""
    print("Eliminando todos los datos existentes...")
    
    try:
        # Borrar en orden para respetar foreign keys usando SQLAlchemy ORM
        print("  - Eliminando comentarios...")
        db.query(Comment).delete()
        
        print("  - Eliminando anuncios...")
        db.query(Announcement).delete()
        
        print("  - Eliminando entregas...")
        db.query(Submission).delete()
        
        print("  - Eliminando tareas...")
        db.query(Task).delete()
        
        print("  - Eliminando perfiles de estudiantes...")
        db.query(StudentProfile).delete()
        
        print("  - Eliminando inscripciones...")
        db.query(Enrollment).delete()
        
        print("  - Eliminando cursos...")
        db.query(Course).delete()
        
        print("  - Eliminando usuarios (estudiantes, profesores)...")
        # Borrar todos los usuarios excepto administradores usando ORM
        db.query(User).filter(User.role != UserRole.ADMINISTRADOR).delete()
        
        db.commit()
        print("[OK] Todos los datos han sido eliminados")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al eliminar datos: {e}")
        import traceback
        traceback.print_exc()
        raise

def create_professors_and_courses(db):
    """Crea los profesores y sus cursos según la estructura PAES"""
    print("\nCreando profesores y cursos PAES...")
    
    professors_created = []
    courses_created = []
    
    for subject, config in PAES_STRUCTURE.items():
        # Crear profesor
        professor = User(
            email=config["professor_email"],
            full_name=config["professor_name"],
            hashed_password=get_password_hash("profesor123"),  # Contraseña por defecto
            role=UserRole.DOCENTE,
            is_active=True
        )
        db.add(professor)
        db.flush()  # Para obtener el ID
        
        professors_created.append(professor)
        print(f"\n  Profesor creado: {professor.full_name} ({professor.email})")
        
        # Crear cursos del profesor
        for course_data in config["courses"]:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                subject=course_data["subject"],
                paes_topic=course_data["paes_topic"],
                owner_id=professor.id,
                created_at=datetime.now(timezone.utc)
            )
            db.add(course)
            courses_created.append(course)
            print(f"    - Curso creado: {course.title} [{course.subject}] - {course.paes_topic}")
    
    db.commit()
    
    print(f"\n[OK] Creados {len(professors_created)} profesores")
    print(f"[OK] Creados {len(courses_created)} cursos")
    
    return professors_created, courses_created

def main():
    """Función principal"""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("Configuracion de Estructura PAES - Plataforma Preuniversitaria")
        print("=" * 70)
        print()
        
        # Paso 1: Eliminar todos los datos
        delete_all_data(db)
        
        # Paso 2: Crear profesores y cursos
        professors, courses = create_professors_and_courses(db)
        
        print("\n" + "=" * 70)
        print("Configuracion completada exitosamente!")
        print("=" * 70)
        print("\nResumen:")
        print(f"  - Profesores: {len(professors)}")
        print(f"  - Cursos: {len(courses)}")
        print("\nCredenciales de acceso:")
        for prof in professors:
            print(f"  - {prof.full_name}: {prof.email} / profesor123")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error durante la configuracion: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

