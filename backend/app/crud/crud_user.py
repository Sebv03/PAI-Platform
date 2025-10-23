# backend/app/crud/crud_user.py
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate




def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario en la base de datos.
    """
    user_data = user_in.model_dump()

    # --- LÍNEA DE DEBUG ---
    print(f"DEBUG: Contraseña recibida: '{user_data['password']}'")
    print(f"DEBUG: Longitud en bytes: {len(user_data['password'].encode('utf-8'))}")
    # ----------------------

    hashed_password = get_password_hash(user_data["password"])
    
    user_data["hashed_password"] = hashed_password
    del user_data["password"]

    db_user = User(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    """
    Autentica a un usuario.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ... al final de crud_user.py
def get_user_by_id(db: Session, *, user_id: int) -> User | None:
    """
    Busca un usuario por su ID.
    """
    return db.query(User).filter(User.id == user_id).first()