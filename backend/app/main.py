# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from app.db.base import Base
from app.db.session import engine # <-- Importa el engine desde session.py
from app.core.config import settings # <-- Importa settings

# Importamos todos los routers
from app.api.endpoints import users, login, courses, enrollments, tasks

# --- Función para crear las tablas ---
def create_tables():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine) # Usa el engine de session.py
    print("Tablas creadas.")

create_tables()

# --- Instancia de la aplicación FastAPI ---
app = FastAPI(
    title="Plataforma Académica Inteligente (PAI) API",
    description="API para la gestión de cursos, usuarios, tareas y entregas.",
    version="0.1.0",
)

# --- Configuración de CORS ---
origins = [
    "http://localhost",
    "http://localhost:5173", # Frontend de React
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusión de Routers ---
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(login.router, prefix="/login", tags=["Login"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to PAI API! Visit /docs for API documentation."}