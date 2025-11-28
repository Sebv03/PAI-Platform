# 🚀 Prompt de Instalación Completa - Plataforma PAI

## Descripción

Este documento proporciona las instrucciones exactas para instalar la plataforma PAI desde cero y configurarla con todos los datos predefinidos (profesores, estudiantes, cursos, tareas, entregas, etc.) exactamente como están configurados actualmente.

## Requisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Node.js 16 o superior
- Git

## Pasos de Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Sebv03/PAI-Platform.git
cd PAI-Platform
```

### 2. Configurar Backend

```bash
cd backend
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar Base de Datos PostgreSQL

```bash
# Crear base de datos
psql -U postgres
CREATE DATABASE pai_platform;
\q
```

### 4. Configurar Variables de Entorno

Crear archivo `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/pai_platform
SECRET_KEY=tu_secret_key_muy_segura_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**IMPORTANTE:** Reemplazar `tu_password` con tu contraseña real de PostgreSQL.

### 5. Ejecutar Script de Configuración Completa

Este es el comando clave que configura todo automáticamente:

```bash
# Asegúrate de estar en el directorio backend con el venv activado
cd backend
python setup_complete_platform.py
```

Este script:
- ✅ Crea todas las tablas de la base de datos
- ✅ Crea el usuario administrador
- ✅ Crea 4 profesores (Matemáticas, Lenguaje, Ciencias, Historia)
- ✅ Crea 15 cursos PAES predefinidos
- ✅ Crea 200 estudiantes con perfiles completos
- ✅ Crea 912 inscripciones en cursos
- ✅ Crea 97 tareas distribuidas
- ✅ Crea 3,278 entregas con calificaciones

**Tiempo estimado:** 2-5 minutos

### 6. Configurar Frontend

```bash
# Desde la raíz del proyecto
cd frontend
npm install

# Crear archivo .env
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 7. Configurar ML Service

```bash
cd ml-service
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

## Iniciar la Plataforma

### Terminal 1: Backend

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

### Terminal 3: ML Service

```bash
cd ml-service
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python main.py
```

## Credenciales de Acceso

### Administrador
- **Email:** `admin@pai.cl`
- **Password:** `admin123`

### Profesores
Todos los profesores tienen la contraseña: `profesor123`

- **Matemáticas:** `profesor.matematicas@pai.cl`
- **Lenguaje:** `profesor.lenguaje@pai.cl`
- **Ciencias:** `profesor.ciencias@pai.cl`
- **Historia:** `profesor.historia@pai.cl`

### Estudiante de Ejemplo
- **Email:** `juan.perez.0@estudiante.pai.cl`
- **Password:** `estudiante123`

**NOTA:** Todos los 200 estudiantes tienen la misma contraseña: `estudiante123`

## Datos Generados

Después de ejecutar el script `setup_complete_platform.py`, tendrás:

- **4 Profesores** (uno por asignatura)
- **15 Cursos PAES**:
  - Matemáticas: 4 cursos
  - Lenguaje: 5 cursos
  - Ciencias: 3 cursos
  - Historia: 3 cursos
- **200 Estudiantes** (14-18 años, 1° a 4° medio)
- **912 Inscripciones**
- **97 Tareas**
- **3,278 Entregas** con calificaciones

## Verificación

1. **Backend API:** http://localhost:8000/docs
2. **Frontend:** http://localhost:5173
3. **ML Service:** http://localhost:8001/health

## Reinstalar/Resetear

Si necesitas reinstalar desde cero:

```bash
cd backend
venv\Scripts\activate  # Windows
python setup_complete_platform.py
```

El script detectará datos existentes, los eliminará y recreará todo desde cero.

## Características del Script

- ✅ **Reproducible:** Usa seed fijo (42) para generar siempre los mismos datos
- ✅ **Idempotente:** Puede ejecutarse múltiples veces sin problemas
- ✅ **Completo:** Configura toda la plataforma en un solo paso
- ✅ **Informative:** Muestra progreso detallado y resumen final

## Notas Importantes

1. **Seguridad:** Las contraseñas por defecto son solo para desarrollo. Cambiar todas en producción.
2. **Datos Reproducibles:** El script usa seeds fijos para garantizar datos consistentes.
3. **Backup:** Hacer backup antes de ejecutar si tienes datos importantes.
4. **Entrenamiento ML:** Después de instalar, entrenar el modelo ML desde el Admin Dashboard.

---

**Archivo de referencia completo:** Ver `GUIA_INSTALACION_COMPLETA.md` para detalles adicionales y solución de problemas.



