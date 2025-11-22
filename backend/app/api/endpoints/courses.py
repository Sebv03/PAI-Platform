from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_course
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseUpdate
from app.models.user import User # Importa el modelo User
from app.models.user import UserRole # Importa UserRole para la comparación de roles

router = APIRouter()

# ----------------- Endpoint para OBTENER todos los cursos (Solo Admin) -----------------
@router.get("/", response_model=List[CourseSchema])
async def read_all_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtiene una lista de TODOS los cursos.
    (Protegido: Solo para Administradores).
    """
    from app.crud import crud_user
    from datetime import datetime
    
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver todos los cursos."
        )
    courses = crud_course.get_courses(db, skip=skip, limit=limit)
    
    # Formatear respuesta con información del profesor
    result = []
    for course in courses:
        owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "owner_id": course.owner_id,
            "owner_name": None,
            "owner_email": None,
            "created_at": None
        }
        if owner:
            course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
            course_dict["owner_email"] = owner.email
        if hasattr(course, 'created_at') and course.created_at:
            course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
        result.append(CourseSchema(**course_dict))
    
    return result

# ----------------- Endpoint para CREAR un curso (Solo Docente/Admin) -----------------
@router.post("/", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: CourseCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Crea un nuevo curso, asociado al usuario autenticado (solo docentes o administradores).
    """
    if current_user.role not in [UserRole.DOCENTE, UserRole.ADMINISTRADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes o administradores pueden crear cursos.",
        )
    
    from app.crud import crud_user
    from datetime import datetime
    
    course = crud_course.create_user_course(db, course_in=course_in, owner=current_user)
    
    # Formatear respuesta con información del profesor
    owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "owner_id": course.owner_id,
        "owner_name": None,
        "owner_email": None,
        "created_at": None
    }
    if owner:
        course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
        course_dict["owner_email"] = owner.email
    if hasattr(course, 'created_at') and course.created_at:
        course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
    
    return CourseSchema(**course_dict)

# ----------------- Endpoint para OBTENER los cursos del usuario actual (Docente) -----------------
@router.get("/me", response_model=List[CourseSchema])
async def read_current_user_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtiene todos los cursos creados por el usuario docente autenticado.
    """
    from app.crud import crud_user
    from datetime import datetime
    
    if current_user.role != UserRole.DOCENTE:
        # Devuelve una lista vacía si el usuario no es docente (ej. un estudiante)
        return [] 
    
    # Llama a la función CRUD que filtra por owner_id
    courses = crud_course.get_courses_by_owner(db, owner_id=current_user.id)
    
    # Formatear respuesta con información del profesor
    result = []
    for course in courses:
        owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "owner_id": course.owner_id,
            "owner_name": None,
            "owner_email": None,
            "created_at": None
        }
        if owner:
            course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
            course_dict["owner_email"] = owner.email
        if hasattr(course, 'created_at') and course.created_at:
            course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
        result.append(CourseSchema(**course_dict))
    
    return result

# ----------------- Endpoint para OBTENER cursos DISPONIBLES para estudiantes (no inscritos) -----------------
@router.get("/available", response_model=List[CourseSchema])
async def read_available_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtiene la lista de cursos disponibles (no inscritos) para el estudiante autenticado.
    Solo estudiantes pueden acceder a este endpoint.
    """
    from app.crud import crud_user
    from datetime import datetime
    
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los estudiantes pueden ver cursos disponibles."
        )
    
    courses = crud_course.get_available_courses_for_student(
        db, student_id=current_user.id, skip=skip, limit=limit
    )
    
    # Formatear respuesta con información del profesor
    result = []
    for course in courses:
        owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "owner_id": course.owner_id,
            "owner_name": None,
            "owner_email": None,
            "created_at": None
        }
        if owner:
            course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
            course_dict["owner_email"] = owner.email
        if hasattr(course, 'created_at') and course.created_at:
            course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
        result.append(CourseSchema(**course_dict))
    
    return result

# ----------------- Endpoint para OBTENER un curso por ID -----------------
@router.get("/{course_id}", response_model=CourseSchema)
async def read_course_by_id(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) 
) -> Any:
    """
    Obtiene los detalles de un curso específico por su ID.
    (Cualquier usuario autenticado puede ver los detalles de un curso).
    """
    from app.crud import crud_user
    from datetime import datetime
    
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )
    
    # Obtener información del propietario (profesor)
    owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
    
    # Construir respuesta con información del profesor
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "owner_id": course.owner_id,
        "owner_name": None,
        "owner_email": None,
        "created_at": None
    }
    
    if owner:
        course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
        course_dict["owner_email"] = owner.email
    
    if hasattr(course, 'created_at') and course.created_at:
        course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
    
    return CourseSchema(**course_dict)

# ----------------- Endpoint para ACTUALIZAR un curso (Solo Docente/Admin) -----------------
@router.put("/{course_id}", response_model=CourseSchema)
async def update_existing_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Actualiza un curso existente (solo el propietario o un administrador).
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )
    
    # Solo el propietario del curso o un administrador puede actualizarlo
    if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este curso."
        )
    
    from app.crud import crud_user
    from datetime import datetime
    
    course = crud_course.update_course(db, db_obj=course, obj_in=course_in)
    
    # Formatear respuesta con información del profesor
    owner = crud_user.get_user_by_id(db, user_id=course.owner_id)
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "owner_id": course.owner_id,
        "owner_name": None,
        "owner_email": None,
        "created_at": None
    }
    if owner:
        course_dict["owner_name"] = owner.full_name or f"Usuario {owner.id}"
        course_dict["owner_email"] = owner.email
    if hasattr(course, 'created_at') and course.created_at:
        course_dict["created_at"] = course.created_at.isoformat() if isinstance(course.created_at, datetime) else str(course.created_at)
    
    return CourseSchema(**course_dict)

# ----------------- Endpoint para ELIMINAR un curso (Solo Docente/Admin) -----------------
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> None: # <-- El tipo de retorno es None
    """
    Elimina un curso existente (solo el propietario o un administrador).
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )
    
    if course.owner_id != current_user.id and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este curso."
        )
    
    crud_course.delete_course(db, id=course_id)
    
    return None # <-- No se devuelve NADA en un 204