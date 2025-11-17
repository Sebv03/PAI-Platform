# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

# La clase Base que tus modelos usarán para heredar
Base = declarative_base()

# Importa el paquete de modelos. Esto asegura que todos los modelos se registren
# con Base.metadata, pero evita importaciones directas que puedan causar ciclos.
import app.models # <--- ¡CAMBIO CLAVE AQUÍ!