# 🚀 Guía Rápida - Iniciar Servidores Locales

Esta guía te ayudará a iniciar todos los servicios de la plataforma PAI en tu entorno local.

## 📌 Resumen Ejecutivo

**Necesitas 4 terminales abiertas:**

| Terminal | Servicio | Comando | Puerto |
|----------|----------|---------|--------|
| 1 | Base de Datos | `docker-compose up -d db` | 5433 |
| 2 | Backend | `uvicorn app.main:app --reload --port 8000` | 8000 |
| 3 | ML Service | `python main.py` | 8001 |
| 4 | Frontend | `npm run dev` | 5173 |

**URLs importantes:**
- 🌐 Frontend: http://localhost:5173
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🤖 ML Service: http://localhost:8001

---

## 📋 Requisitos Previos

- **Python 3.11+** instalado
- **Node.js 18+** y npm instalados
- **PostgreSQL** instalado (o Docker para la base de datos)
- **Git** instalado

---

## ⚡ Inicio Rápido (3 Pasos)

### 1️⃣ Iniciar Base de Datos

**Opción A: Con Docker (Recomendado)**
```bash
# Desde la raíz del proyecto
docker-compose up -d db

# Verificar que está corriendo
docker-compose ps db
```

**Opción B: PostgreSQL Local**
```bash
# Asegúrate de que PostgreSQL esté corriendo en el puerto 5433
# Con usuario: postgres, password: 123456, base de datos: pai_db

# Si necesitas crear la base de datos:
createdb -U postgres -p 5433 pai_db
```

### 2️⃣ Iniciar Backend y ML Service

**Terminal 1 - Backend:**
```bash
cd backend

# Activar entorno virtual (si lo tienes)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --port 8000

# Deberías ver: "Uvicorn running on http://0.0.0.0:8000"
```

**Terminal 2 - ML Service:**
```bash
cd ml-service

# Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# Iniciar servidor
python main.py

# Deberías ver: "Uvicorn running on http://0.0.0.0:8001"
```

### 3️⃣ Iniciar Frontend

**Terminal 3 - Frontend:**
```bash
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar servidor de desarrollo
npm run dev

# Deberías ver: "Local: http://localhost:5173/"
```

---

## ✅ Verificar que Todo Funciona

Abre tu navegador y verifica:

- **Frontend**: http://localhost:5173
  - Deberías ver la página de inicio de la plataforma
  
- **Backend API**: http://localhost:8000
  - Deberías ver: `{"message": "Welcome to PAI Platform API"}`
  
- **API Docs (Swagger)**: http://localhost:8000/docs
  - Interfaz interactiva para probar los endpoints
  
- **ML Service**: http://localhost:8001
  - Deberías ver: `{"message": "PAI ML Service is running"}`
  
- **ML Service Docs**: http://localhost:8001/docs
  - Documentación del servicio de ML

### Probar Login

1. Ve a http://localhost:5173
2. Haz clic en "Iniciar Sesión"
3. Si creaste un administrador, usa esas credenciales
4. Si no, primero ejecuta: `cd backend && python create_admin.py`

---

## 🔧 Configuración Inicial (Solo Primera Vez)

### Crear Usuario Administrador

```bash
cd backend
python create_admin.py
```

### (Opcional) Poblar Datos de Prueba

```bash
cd backend
python populate_historical_data.py
```

---

## 📝 Comandos Útiles

### Detener Servicios

- **Backend/ML Service**: `Ctrl + C` en la terminal
- **Frontend**: `Ctrl + C` en la terminal
- **Base de Datos (Docker)**: `docker-compose down`

### Ver Logs de Base de Datos

```bash
docker-compose logs -f db
```

### Reiniciar Base de Datos

```bash
docker-compose restart db
```

---

## 🐛 Solución de Problemas

### Error: Puerto ya en uso

Si un puerto está ocupado, puedes cambiarlo:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8002
```

**ML Service:**
Edita `ml-service/main.py` y cambia el puerto en `uvicorn.run()`

**Frontend:**
Edita `frontend/vite.config.js` y agrega:
```js
export default defineConfig({
  server: {
    port: 5174
  }
})
```

### Error: No se conecta a la base de datos

Verifica que PostgreSQL esté corriendo:
```bash
# Con Docker
docker-compose ps db

# Ver logs
docker-compose logs db
```

### Error: Módulos no encontrados

Asegúrate de instalar las dependencias:
```bash
# Backend
cd backend
pip install -r requirements.txt

# ML Service
cd ml-service
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📚 Estructura de Servicios

```
┌─────────────┐
│  Frontend   │  →  http://localhost:5173
│  (React)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │  →  http://localhost:8000
│  (FastAPI)  │
└──────┬──────┘
       │
       ├──→ ┌─────────────┐
       │    │ ML Service  │  →  http://localhost:8001
       │    │  (FastAPI)  │
       │    └─────────────┘
       │
       ↓
┌─────────────┐
│ PostgreSQL  │  →  localhost:5433
│  (Database) │
└─────────────┘
```

---

## 🎯 Orden de Inicio Recomendado

1. **Base de datos** (PostgreSQL)
2. **Backend** (FastAPI - puerto 8000)
3. **ML Service** (FastAPI - puerto 8001)
4. **Frontend** (React - puerto 5173)

---

## 💡 Tips

- Mantén las terminales abiertas mientras trabajas
- El backend y ML service tienen `--reload` para recargar automáticamente
- El frontend de Vite también recarga automáticamente
- Usa `Ctrl + C` para detener cualquier servidor

---

**¡Listo! 🎉 Ya puedes empezar a desarrollar.**

