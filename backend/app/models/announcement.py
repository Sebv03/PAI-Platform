# backend/app/models/announcement.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from app.db.base import Base

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"), nullable=True)
    
    # Claves foráneas
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relaciones ---
    course = relationship("Course", back_populates="announcements")
    author = relationship("User", back_populates="announcements")
    comments = relationship("Comment", back_populates="announcement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Announcement(id={self.id}, title='{self.title}', course_id={self.course_id})>"

