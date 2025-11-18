# backend/app/schemas/announcement.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# Esquema base para comunicados
class AnnouncementBase(BaseModel):
    title: str
    content: str

# Esquema para crear un comunicado
class AnnouncementCreate(AnnouncementBase):
    pass

# Esquema para actualizar un comunicado
class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# Esquema para leer un comunicado (con información del autor)
class Announcement(AnnouncementBase):
    id: int
    course_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Esquema para comentarios
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    announcement_id: int
    author_id: int
    created_at: datetime
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Esquema extendido que incluye comentarios
class AnnouncementWithComments(Announcement):
    comments: List[Comment] = []

