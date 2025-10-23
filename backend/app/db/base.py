# backend/app/db/base.py

from sqlalchemy.orm import DeclarativeBase

# Esta será la clase base de la que heredarán todos nuestros modelos.
# NO debe importar ningún modelo aquí.
class Base(DeclarativeBase):
    pass