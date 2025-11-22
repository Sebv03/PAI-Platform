# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
from pathlib import Path

# Importa los routers de la API
from app.api.endpoints import users, courses, tasks, enrollments, submissions, announcements, ml_predictions, student_profiles
from app.api.endpoints.login import router as login_router

from app.core.config import settings # <-- Importa la configuración
from app.db.base import Base
from app.db.session import engine # <-- Importa el engine de la sesión

# --- Función para crear las tablas ---
def create_tables():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine) # Usa el engine de session.py
    print("Tablas creadas.")

create_tables()

# --- Instancia de la aplicación FastAPI ---
app = FastAPI(
    title=settings.PROJECT_NAME, # <-- Usa el nombre del proyecto de config
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # <-- Usa la ruta de config
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS], # <-- Usa los orígenes de config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Crear directorio de uploads si no existe ---
from app.core.config import settings
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

# --- Montar directorio estático para servir archivos (opcional, para desarrollo) ---
# En producción, usa un servidor web como Nginx para servir archivos estáticos
# app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- Inclusión de Routers ---
app.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
app.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
app.include_router(announcements.router, prefix="/announcements", tags=["announcements"])
app.include_router(ml_predictions.router, prefix="/ml", tags=["ML Predictions"])
app.include_router(student_profiles.router, prefix=f"{settings.API_V1_STR}/student-profiles", tags=["Student Profiles"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to PAI API! Visit /docs for API documentation."}