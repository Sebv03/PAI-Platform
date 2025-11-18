# backend/app/api/endpoints/announcements.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_announcement, crud_comment, crud_course, crud_enrollment, crud_user
from app.schemas.announcement import Announcement, AnnouncementCreate, AnnouncementUpdate, Comment, CommentCreate
from app.models.user import User as UserModel
from app.models.user import UserRole

router = APIRouter()

# ----------------- Endpoint para OBTENER comunicados de un curso -----------------
@router.get("/course/{course_id}", response_model=List[Announcement])
async def read_announcements_by_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene todos los comunicados de un curso específico.
    Acceso: Estudiantes inscritos, docente del curso, o admin.
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    # Verificar permisos
    if current_user.role == UserRole.ADMINISTRADOR or current_user.id == course.owner_id:
        # Admin o docente propietario pueden ver todos los comunicados
        pass
    elif current_user.role == UserRole.ESTUDIANTE:
        # Estudiantes solo si están inscritos
        enrollment = crud_enrollment.get_enrollment_by_user_and_course(
            db, student_id=current_user.id, course_id=course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes estar inscrito en el curso para ver los comunicados"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los comunicados de este curso"
        )
    
    announcements = crud_announcement.get_announcements_by_course(db, course_id=course_id)
    
    # Agregar información del autor
    result = []
    for announcement in announcements:
        author = crud_user.get_user_by_id(db, user_id=announcement.author_id)
        announcement_dict = {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "course_id": announcement.course_id,
            "author_id": announcement.author_id,
            "created_at": announcement.created_at,
            "updated_at": getattr(announcement, 'updated_at', None),
            "author_name": None,
            "author_email": None
        }
        if author:
            announcement_dict["author_name"] = author.full_name or f"Usuario {author.id}"
            announcement_dict["author_email"] = author.email
        result.append(Announcement(**announcement_dict))
    
    return result

# ----------------- Endpoint para CREAR un comunicado -----------------
@router.post("/course/{course_id}", response_model=Announcement, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    course_id: int,
    announcement_in: AnnouncementCreate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Crea un nuevo comunicado en un curso.
    Solo el docente propietario del curso o un admin pueden crear comunicados.
    """
    course = crud_course.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    # Verificar permisos: solo docente propietario o admin
    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el docente del curso puede crear comunicados"
        )
    
    announcement = crud_announcement.create_announcement(
        db, announcement_in=announcement_in, course_id=course_id, author_id=current_user.id
    )
    
    # Agregar información del autor
    author = crud_user.get_user_by_id(db, user_id=announcement.author_id)
    announcement_dict = {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "course_id": announcement.course_id,
        "author_id": announcement.author_id,
        "created_at": announcement.created_at,
        "updated_at": announcement.updated_at,
        "author_name": author.full_name if author else None,
        "author_email": author.email if author else None
    }
    
    return Announcement(**announcement_dict)

# ----------------- Endpoint para ACTUALIZAR un comunicado -----------------
@router.put("/{announcement_id}", response_model=Announcement)
async def update_announcement(
    announcement_id: int,
    announcement_in: AnnouncementUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Actualiza un comunicado existente.
    Solo el autor del comunicado, el docente del curso, o un admin pueden actualizarlo.
    """
    db_announcement = crud_announcement.get_announcement_by_id(db, announcement_id=announcement_id)
    if not db_announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado no encontrado")
    
    course = crud_course.get_course_by_id(db, course_id=db_announcement.course_id)
    
    # Verificar permisos
    if (current_user.role != UserRole.ADMINISTRADOR and 
        current_user.id != course.owner_id and 
        current_user.id != db_announcement.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este comunicado"
        )
    
    announcement = crud_announcement.update_announcement(
        db, db_announcement=db_announcement, announcement_in=announcement_in
    )
    
    # Agregar información del autor
    author = crud_user.get_user_by_id(db, user_id=announcement.author_id)
    announcement_dict = {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "course_id": announcement.course_id,
        "author_id": announcement.author_id,
        "created_at": announcement.created_at,
        "updated_at": announcement.updated_at,
        "author_name": author.full_name if author else None,
        "author_email": author.email if author else None
    }
    
    return Announcement(**announcement_dict)

# ----------------- Endpoint para ELIMINAR un comunicado -----------------
@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Elimina un comunicado.
    Solo el docente del curso o un admin pueden eliminarlo.
    """
    db_announcement = crud_announcement.get_announcement_by_id(db, announcement_id=announcement_id)
    if not db_announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado no encontrado")
    
    course = crud_course.get_course_by_id(db, course_id=db_announcement.course_id)
    
    # Verificar permisos: solo docente propietario o admin
    if current_user.role != UserRole.ADMINISTRADOR and current_user.id != course.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el docente del curso puede eliminar comunicados"
        )
    
    crud_announcement.delete_announcement(db, announcement_id=announcement_id)
    return None

# ----------------- Endpoint para OBTENER comentarios de un comunicado -----------------
@router.get("/{announcement_id}/comments", response_model=List[Comment])
async def read_comments_by_announcement(
    announcement_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Obtiene todos los comentarios de un comunicado.
    Acceso: Estudiantes inscritos, docente del curso, o admin.
    """
    announcement = crud_announcement.get_announcement_by_id(db, announcement_id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado no encontrado")
    
    course = crud_course.get_course_by_id(db, course_id=announcement.course_id)
    
    # Verificar permisos (mismo que para ver comunicados)
    if current_user.role == UserRole.ADMINISTRADOR or current_user.id == course.owner_id:
        pass
    elif current_user.role == UserRole.ESTUDIANTE:
        enrollment = crud_enrollment.get_enrollment_by_user_and_course(
            db, student_id=current_user.id, course_id=announcement.course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes estar inscrito en el curso para ver los comentarios"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los comentarios"
        )
    
    comments = crud_comment.get_comments_by_announcement(db, announcement_id=announcement_id)
    
    # Agregar información del autor
    result = []
    for comment in comments:
        author = crud_user.get_user_by_id(db, user_id=comment.author_id)
        comment_dict = {
            "id": comment.id,
            "content": comment.content,
            "announcement_id": comment.announcement_id,
            "author_id": comment.author_id,
            "created_at": comment.created_at,
            "author_name": author.full_name if author else None,
            "author_email": author.email if author else None
        }
        result.append(Comment(**comment_dict))
    
    return result

# ----------------- Endpoint para CREAR un comentario -----------------
@router.post("/{announcement_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    announcement_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    Crea un nuevo comentario en un comunicado.
    Acceso: Estudiantes inscritos, docente del curso, o admin.
    """
    announcement = crud_announcement.get_announcement_by_id(db, announcement_id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado no encontrado")
    
    course = crud_course.get_course_by_id(db, course_id=announcement.course_id)
    
    # Verificar permisos
    if current_user.role == UserRole.ADMINISTRADOR or current_user.id == course.owner_id:
        pass
    elif current_user.role == UserRole.ESTUDIANTE:
        enrollment = crud_enrollment.get_enrollment_by_user_and_course(
            db, student_id=current_user.id, course_id=announcement.course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes estar inscrito en el curso para comentar"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para comentar"
        )
    
    comment = crud_comment.create_comment(
        db, comment_in=comment_in, announcement_id=announcement_id, author_id=current_user.id
    )
    
    # Agregar información del autor
    author = crud_user.get_user_by_id(db, user_id=comment.author_id)
    comment_dict = {
        "id": comment.id,
        "content": comment.content,
        "announcement_id": comment.announcement_id,
        "author_id": comment.author_id,
        "created_at": comment.created_at,
        "author_name": author.full_name if author else None,
        "author_email": author.email if author else None
    }
    
    return Comment(**comment_dict)

# ----------------- Endpoint para ELIMINAR un comentario -----------------
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Elimina un comentario.
    Solo el autor del comentario, el docente del curso, o un admin pueden eliminarlo.
    """
    db_comment = crud_comment.get_comment_by_id(db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
    
    announcement = crud_announcement.get_announcement_by_id(db, announcement_id=db_comment.announcement_id)
    course = crud_course.get_course_by_id(db, course_id=announcement.course_id)
    
    # Verificar permisos
    if (current_user.role != UserRole.ADMINISTRADOR and 
        current_user.id != course.owner_id and 
        current_user.id != db_comment.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este comentario"
        )
    
    crud_comment.delete_comment(db, comment_id=comment_id)
    return None

