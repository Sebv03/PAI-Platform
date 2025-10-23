# backend/app/models/user.py
from __future__ import annotations # Keep this for relationships
import enum # <-- Import enum
from typing import List
from sqlalchemy import Column, Integer, String, Boolean, Enum as EnumSQL # <-- Import EnumSQL
from sqlalchemy.orm import relationship

from app.db.base import Base

# --- ENSURE THIS ENUM IS DEFINED HERE ---
class UserRole(enum.Enum):
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    PSICOPEDAGOGO = "psicopedagogo"
    ADMINISTRADOR = "administrador"
# ----------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    # --- Make sure the 'role' column uses EnumSQL(UserRole) ---
    role = Column(EnumSQL(UserRole), default=UserRole.ESTUDIANTE, nullable=False)
    # -----------------------------------------------------------
    is_active = Column(Boolean, default=True)

    # Relationships (ensure these are correct)
    courses = relationship("Course", back_populates="owner")
    enrollments = relationship("Enrollment", back_populates="user")
    # Add other relationships like submissions if you have them
    submissions = relationship("Submission", back_populates="user")
# IMPORTANT: Ensure this file does NOT import anything from app.schemas.user