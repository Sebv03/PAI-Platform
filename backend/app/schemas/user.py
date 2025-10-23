# backend/app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date
from app.models.user import UserRole # <-- Ensure this import is present

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: UserRole # <-- Uses the imported UserRole
    is_active: bool
    birth_date: Optional[date] = None # Added based on previous examples

    class Config:
        from_attributes = True