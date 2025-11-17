# backend/app/crud/crud_user.py
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.security import get_password_hash, verify_password # <-- ¡AQUÍ IMPORTAMOS verify_password!
from app.models.user import User # El modelo de usuario de la DB
from app.schemas.user import UserCreate, UserUpdate # Los esquemas de usuario de Pydantic

# ----------------- Obtener un usuario por ID -----------------
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID.
    """
    return db.query(User).filter(User.id == user_id).first()

# ----------------- Obtener un usuario por email -----------------
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su dirección de correo electrónico.
    """
    return db.query(User).filter(User.email == email).first()

# ----------------- Obtener todos los usuarios -----------------
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Obtiene una lista de todos los usuarios.
    """
    return db.query(User).offset(skip).limit(limit).all()

# ----------------- Crear un nuevo usuario -----------------
def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario con la contraseña hasheada.
    """
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ----------------- Autenticar un usuario -----------------
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Autentica un usuario verificando su email y contraseña.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user # Devuelve el usuario si la autenticación es exitosa

# ----------------- Actualizar un usuario existente -----------------
def update_user(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
    """
    Actualiza un usuario existente en la base de datos.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# ----------------- Eliminar un usuario -----------------
def delete_user(db: Session, user_id: int) -> Optional[User]:
    """
    Elimina un usuario por su ID.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user