# backend/app/crud/crud_announcement.py
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate

# ----------------- Crear un comunicado -----------------
def create_announcement(db: Session, announcement_in: AnnouncementCreate, course_id: int, author_id: int) -> Announcement:
    """
    Crea un nuevo comunicado en un curso.
    """
    db_announcement = Announcement(
        title=announcement_in.title,
        content=announcement_in.content,
        course_id=course_id,
        author_id=author_id
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

# ----------------- Obtener comunicados por curso -----------------
def get_announcements_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[Announcement]:
    """
    Obtiene todos los comunicados de un curso específico, ordenados por fecha de creación (más recientes primero).
    """
    return db.query(Announcement).filter(
        Announcement.course_id == course_id
    ).order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()

# ----------------- Obtener un comunicado por ID -----------------
def get_announcement_by_id(db: Session, announcement_id: int) -> Optional[Announcement]:
    """
    Obtiene un comunicado específico por su ID.
    """
    return db.query(Announcement).filter(Announcement.id == announcement_id).first()

# ----------------- Actualizar un comunicado -----------------
def update_announcement(db: Session, db_announcement: Announcement, announcement_in: AnnouncementUpdate) -> Announcement:
    """
    Actualiza un comunicado existente.
    """
    from datetime import datetime
    update_data = announcement_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_announcement, field, value)
    
    # Actualizar manualmente el campo updated_at
    db_announcement.updated_at = datetime.utcnow()
    
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

# ----------------- Eliminar un comunicado -----------------
def delete_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    """
    Elimina un comunicado específico por su ID.
    """
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if db_announcement:
        db.delete(db_announcement)
        db.commit()
    return db_announcement

