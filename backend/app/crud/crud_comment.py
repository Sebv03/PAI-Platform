# backend/app/crud/crud_comment.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.comment import Comment
from app.schemas.announcement import CommentCreate

# ----------------- Crear un comentario -----------------
def create_comment(db: Session, comment_in: CommentCreate, announcement_id: int, author_id: int) -> Comment:
    """
    Crea un nuevo comentario en un comunicado.
    """
    db_comment = Comment(
        content=comment_in.content,
        announcement_id=announcement_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# ----------------- Obtener comentarios por comunicado -----------------
def get_comments_by_announcement(db: Session, announcement_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
    """
    Obtiene todos los comentarios de un comunicado específico, ordenados por fecha de creación (más antiguos primero).
    """
    return db.query(Comment).filter(
        Comment.announcement_id == announcement_id
    ).order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()

# ----------------- Obtener un comentario por ID -----------------
def get_comment_by_id(db: Session, comment_id: int) -> Optional[Comment]:
    """
    Obtiene un comentario específico por su ID.
    """
    return db.query(Comment).filter(Comment.id == comment_id).first()

# ----------------- Eliminar un comentario -----------------
def delete_comment(db: Session, comment_id: int) -> Optional[Comment]:
    """
    Elimina un comentario específico por su ID.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment


