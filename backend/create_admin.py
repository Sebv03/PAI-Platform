"""
Script para crear un usuario administrador
"""

import sys
from pathlib import Path

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_admin_user(email: str = "admin@pai.cl", password: str = "admin123", full_name: str = "Administrador"):
    """Crea un usuario administrador"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin con ese email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            if existing_user.role == UserRole.ADMINISTRADOR:
                print(f"Ya existe un administrador con el email: {email}")
                return existing_user
            else:
                # Actualizar el rol a administrador
                existing_user.role = UserRole.ADMINISTRADOR
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                db.refresh(existing_user)
                print(f"Usuario {email} actualizado a administrador")
                return existing_user
        
        # Crear nuevo administrador
        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMINISTRADOR,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("=" * 60)
        print("ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Email: {email}")
        print(f"Contraseña: {password}")
        print(f"Nombre: {full_name}")
        print()
        print("Puedes iniciar sesión con estas credenciales en:")
        print("http://localhost:5173/login")
        print()
        
        return admin_user
    
    except Exception as e:
        db.rollback()
        print(f"Error al crear administrador: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crear un usuario administrador")
    parser.add_argument("--email", default="admin@pai.cl", help="Email del administrador")
    parser.add_argument("--password", default="admin123", help="Contraseña del administrador")
    parser.add_argument("--name", default="Administrador", help="Nombre completo del administrador")
    
    args = parser.parse_args()
    
    create_admin_user(
        email=args.email,
        password=args.password,
        full_name=args.name
    )

