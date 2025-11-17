# backend/app/models/enrollment.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.sql import text


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_date = Column(DateTime, server_default=text("NOW()"), nullable=False)

    # Foreign Keys
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # --- RELACIONES ---
    # Una inscripción pertenece a un estudiante (User)
    student = relationship("User", back_populates="enrollments") # <--- USA CADENA

    # Una inscripción pertenece a un curso (Course)
    course = relationship("Course", back_populates="enrollments") # <--- USA CADENA

    def __repr__(self):
        return f"<Enrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id})>"