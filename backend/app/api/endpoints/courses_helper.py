# backend/app/api/endpoints/courses_helper.py
"""
Funciones auxiliares para formatear respuestas de cursos
"""
from datetime import datetime
from app.models.course import Course
from app.models.user import User


def format_course_response(course: Course, owner: User = None) -> dict:
    """
    Formatea un curso con toda su información para la respuesta de la API.
    
    Args:
        course: Objeto Course de SQLAlchemy
        owner: Objeto User del propietario (opcional)
    
    Returns:
        Dict con toda la información formateada del curso
    """
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subject": getattr(course, 'subject', None),  # Asignatura (opcional)
        "paes_topic": getattr(course, 'paes_topic', None),  # Temática PAES (opcional)
        "owner_id": course.owner_id,
        "owner_name": None,
        "owner_email": None,
        "created_at": None
    }
    
    # Agregar información del propietario si está disponible
    if owner:
        course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
        course_dict["owner_email"] = owner.email
    
    # Formatear fecha de creación
    if hasattr(course, 'created_at') and course.created_at:
        if isinstance(course.created_at, datetime):
            course_dict["created_at"] = course.created_at.isoformat()
        else:
            course_dict["created_at"] = str(course.created_at)
    
    return course_dict

