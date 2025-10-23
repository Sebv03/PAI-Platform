# backend/app/main.py
from fastapi import FastAPI
# Importamos CORSMiddleware desde fastapi.middleware.cors
from fastapi.middleware.cors import CORSMiddleware 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
# Importamos todos los routers que hemos creado
from app.api.endpoints import users, login, courses, enrollments, tasks

# --- Configuración de la base de datos ---
# Asegúrate de que esta URL de la base de datos sea correcta para tu entorno.
# Si estás usando Docker Compose, "db" es el nombre del servicio de la base de datos.
# Si estás ejecutando PostgreSQL localmente sin Docker, podría ser "localhost" o "127.0.0.1".
DATABASE_URL = "postgresql://sebahenriquez@localhost:5433/pai_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Función para crear las tablas en la base de datos ---
def create_tables():
    """Crea todas las tablas definidas en los modelos SQLAlchemy."""
    Base.metadata.create_all(bind=engine)

# Llama a la función para crear las tablas al iniciar la aplicación.
# Esto asegura que la base de datos esté lista con los esquemas definidos.
create_tables()

# --- Instancia de la aplicación FastAPI ---
app = FastAPI(
    title="Plataforma Académica Inteligente (PAI) API",
    description="API para la gestión de cursos, usuarios, tareas y entregas, con foco en datos para Machine Learning.",
    version="0.1.0",
)

# --- Configuración de CORS (Cross-Origin Resource Sharing) ---
# Esto es crucial para permitir que tu frontend (ej. React en localhost:5173)
# pueda comunicarse con tu backend (en localhost:8000).
origins = [
    "http://localhost",        # Para acceso directo desde localhost
    "http://localhost:5173",   # El origen donde corre tu aplicación frontend de Vite
    "http://127.0.0.1:5173",   # Alternativa común a localhost
    # Puedes añadir otros orígenes aquí si tu frontend se despliega en otro dominio.
    # Ej: "https://tudominio.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Lista de orígenes permitidos
    allow_credentials=True,       # Permite cookies, encabezados de autorización, etc.
    allow_methods=["*"],          # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],          # Permite todas las cabeceras HTTP en las peticiones
)

# --- Inclusión de los Routers de la API ---
# Cada router gestiona un conjunto de endpoints relacionados.
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(login.router, prefix="/login", tags=["Login"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# --- Endpoint de prueba (opcional, para verificar que la API está viva) ---
@app.get("/")
def read_root():
    return {"message": "Welcome to PAI API! Visit /docs for API documentation."}