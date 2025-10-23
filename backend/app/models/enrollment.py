# backend/app/models/enrollment.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.course import Course # Necesitas importar Course si no lo has hecho
from app.models.user import User # Necesitas importar User

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    # --- ASEGÚRATE DE QUE ESTAS RELACIONES ESTÉN PRESENTES Y CORRECTAS ---
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments") # <--- Y ESTO ES CRÍTICO