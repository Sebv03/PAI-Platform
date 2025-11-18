# backend/app/models/comment.py
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from app.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    
    # Claves foráneas
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relaciones ---
    announcement = relationship("Announcement", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, announcement_id={self.announcement_id}, author_id={self.author_id})>"


