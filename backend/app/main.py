# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List # Para la lista de orígenes CORS

# Importa SOLO los routers de la API. Los modelos se importan en app.db.base.py
from app.api.endpoints import users, courses
from app.api.endpoints.login import router as login_router # Importación explícita para login

# --- ¡PREPARADO PARA FUTUROS ROUTERS! ---
from app.api.endpoints import tasks # Descomenta cuando crees tasks.py
# from app.api.endpoints import submissions # Descomenta cuando crees submissions.py
# from app.api.endpoints import enrollments # Descomenta cuando crees enrollments.py


from app.core.config import settings
from app.db.base import Base # Necesario para Base.metadata.create_all
from app.db.session import engine # Necesario para Base.metadata.create_all

# Función para crear las tablas en la base de datos
def create_tables():
    # ¡Importante! Asegúrate de que todos tus modelos estén importados en
    # app.db.base.py para que Base.metadata los detecte aquí.
    Base.metadata.create_all(bind=engine)

# Llamar a la función para crear las tablas
# Considera usar Alembic para migraciones en producción
create_tables()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de la API
app.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])

# --- ¡DESCOMENTA ESTAS LÍNEAS CUANDO HAYAS CREADO LOS ARCHIVOS CORRESPONDIENTES! ---
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# app.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
# app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])


# Rutas de prueba (opcional)
@app.get("/")
def read_root():
    return {"message": "Welcome to PAI Platform API v1"}