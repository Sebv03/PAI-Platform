# backend/app/models/task.py
from __future__ import annotations
from datetime import datetime
from typing import List # <-- ASEGÚRATE QUE ESTA LÍNEA EXISTA
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship("Course", back_populates="tasks")

    # Esta línea necesita 'List'
    submissions = relationship("Submission", back_populates="task")