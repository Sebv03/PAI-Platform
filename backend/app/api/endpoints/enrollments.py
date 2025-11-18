from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_enrollment, crud_course
from app.schemas.enrollment import Enrollment, EnrollmentCreate # Asegúrate que EnrollmentCreate esté en schemas/enrollment.py
from app.schemas.course import Course as CourseSchema # Usamos el schema de Course para la respuesta
from app.models.user import User as UserModel
from app.models.user import UserRole

router = APIRouter()

# ----------------- Endpoint para OBTENER los cursos inscritos del ESTUDIANTE actual -----------------
@router.get("/me/courses", response_model=List[CourseSchema])
async def read_my_enrolled_courses(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene la lista de cursos en los que el estudiante actual está inscrito.
    """
    from app.crud import crud_user
    from datetime import datetime
    
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Solo los estudiantes pueden ver sus cursos inscritos."
        )
        
    courses = crud_enrollment.get_enrolled_courses_by_student(db, student_id=current_user.id)
    
    # Agregar información del profesor a cada curso
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

# Mantener el endpoint anterior por compatibilidad (deprecated)
@router.get("/me", response_model=List[CourseSchema])
async def read_my_enrollments(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    [DEPRECATED] Usa /me/courses en su lugar.
    Obtiene la lista de cursos en los que el estudiante actual está inscrito.
    """
    return await read_my_enrolled_courses(db, current_user)

# ----------------- Endpoint para INSCRIBIR al ESTUDIANTE actual en un curso -----------------
@router.post("/", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
async def enroll_student_in_course(
    enrollment_in: EnrollmentCreate, # Recibimos el course_id desde el schema
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Inscribe al usuario (estudiante) actual en un curso.
    """
    if current_user.role != UserRole.ESTUDIANTE:
        raise HTTPException(status_code=403, detail="Solo los estudiantes pueden inscribirse en cursos.")

    course = crud_course.get_course_by_id(db, course_id=enrollment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # Verificar que el estudiante no sea el dueño del curso (un docente no se inscribe a su propio curso)
    if course.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes inscribirte en tu propio curso.")

    existing = crud_enrollment.get_enrollment_by_user_and_course(db, student_id=current_user.id, course_id=enrollment_in.course_id)
    if existing:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este curso.")
    
    enrollment = crud_enrollment.create_enrollment(db, student_id=current_user.id, course_id=enrollment_in.course_id)
    return enrollment

# ----------------- Endpoint para OBTENER los estudiantes inscritos en un curso (Para Docentes) -----------------
@router.post("/admin", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
async def admin_enroll_student(
    student_id: int = Query(..., description="ID del estudiante a inscribir"),
    course_id: int = Query(..., description="ID del curso"),
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Permite a un administrador inscribir cualquier estudiante en un curso.
    """
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden inscribir estudiantes."
        )
    
    # Verificar que el estudiante existe y es estudiante
    from app.crud import crud_user
    student = crud_user.get_user_by_id(db, user_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    if student.role != UserRole.ESTUDIANTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario especificado no es un estudiante"
        )
    
    # Verificar que el curso existe
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado"
        )
    
    # Verificar si ya está inscrito
    existing = crud_enrollment.get_enrollment_by_user_and_course(
        db, student_id=student_id, course_id=course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estudiante ya está inscrito en este curso"
        )
    
    # Crear la inscripción
    enrollment_in = EnrollmentCreate(course_id=course_id)
    enrollment = crud_enrollment.create_enrollment(
        db, enrollment_in=enrollment_in, student_id=student_id
    )
    
    return enrollment


@router.get("/course/{course_id}/students", response_model=List[Any])
async def read_students_in_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene la lista de estudiantes inscritos en un curso específico.
    Solo el docente propietario del curso o un admin pueden ver esto.
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    # Verificar permisos: solo el docente propietario o admin
    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los estudiantes de este curso"
        )
    
    students = crud_enrollment.get_students_enrolled_in_course(db, course_id=course_id)
    
    # Formatear la respuesta con información relevante del estudiante
    from app.schemas.user import User as UserSchema
    result = []
    for student in students:
        result.append({
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "role": student.role.value if hasattr(student.role, 'value') else str(student.role)
        })
    
    return result