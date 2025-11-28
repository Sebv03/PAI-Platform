# 📋 Guía de Instalación Completa - Plataforma PAI

Esta guía te permitirá instalar la plataforma desde cero y configurarla con todos los datos predefinidos (profesores, estudiantes, cursos, tareas, entregas, etc.) exactamente como están configurados actualmente.

## 🎯 Objetivo

Al finalizar esta guía tendrás:
- ✅ Base de datos completamente configurada
- ✅ 4 profesores (Matemáticas, Lenguaje, Ciencias, Historia)
- ✅ 15 cursos PAES predefinidos
- ✅ 200 estudiantes con perfiles completos
- ✅ 912 inscripciones en cursos
- ✅ 97 tareas distribuidas
- ✅ 3,278 entregas con calificaciones
- ✅ 1 usuario administrador

---

## 📦 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Node.js 16+ (para frontend)
- Git

---

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Sebv03/PAI-Platform.git
cd PAI-Platform
```

### Paso 2: Configurar Backend

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar Base de Datos

1. **Crear base de datos PostgreSQL:**

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE pai_platform;
\q
```

2. **Configurar variables de entorno:**

Crea un archivo `.env` en el directorio `backend/`:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/pai_platform
SECRET_KEY=tu_secret_key_muy_segura_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**IMPORTANTE:** Reemplaza `tu_password` con tu contraseña de PostgreSQL.

### Paso 4: Ejecutar Script de Configuración Completa

Este script creará todo en el orden correcto:

```bash
# Asegúrate de estar en el directorio backend con el venv activado
cd backend

# Ejecutar el script maestro de configuración
python setup_complete_platform.py
```

Este script ejecutará automáticamente:
1. ✅ Creación de tablas
2. ✅ Creación de usuario administrador
3. ✅ Creación de profesores y cursos PAES
4. ✅ Creación de estudiantes con perfiles
5. ✅ Inscripciones en cursos
6. ✅ Creación de tareas
7. ✅ Creación de entregas y calificaciones

**Tiempo estimado:** 2-5 minutos

### Paso 5: Configurar Frontend

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias
npm install

# Crear archivo .env en frontend/
echo "VITE_API_URL=http://localhost:8000" > .env
```

### Paso 6: Configurar ML Service

```bash
# Desde la raíz del proyecto
cd ml-service

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Crear archivo .env o configurar en ml-service/core/config.py
# DATABASE_URL debe apuntar a la misma base de datos
```

---

## 🎮 Iniciar la Plataforma

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
# O: uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

---

## 🔐 Credenciales de Acceso

### Administrador

```
Email: admin@pai.cl
Password: admin123
```

### Profesores

**Profesor de Matemáticas:**
```
Email: profesor.matematicas@pai.cl
Password: profesor123
```

**Profesor de Lenguaje:**
```
Email: profesor.lenguaje@pai.cl
Password: profesor123
```

**Profesor de Ciencias:**
```
Email: profesor.ciencias@pai.cl
Password: profesor123
```

**Profesor de Historia:**
```
Email: profesor.historia@pai.cl
Password: profesor123
```

### Estudiante de Ejemplo

```
Email: juan.perez.0@estudiante.pai.cl
Password: estudiante123
```

**NOTA:** Todos los 200 estudiantes tienen la contraseña: `estudiante123`

---

## 📊 Datos Generados

Después de ejecutar el script, tendrás:

- **4 Profesores** (uno por asignatura)
- **15 Cursos PAES** distribuidos así:
  - Matemáticas: 4 cursos (Números, Álgebra y Funciones, Geometría, Probabilidad y Estadística)
  - Lenguaje: 5 cursos (Comprensión Lectora, Localizar Información, Interpretar y Relacionar, Evaluar y Reflexionar, Tipos de Texto)
  - Ciencias: 3 cursos (Biología, Física, Química)
  - Historia: 3 cursos (Historia en perspectiva, Formación Ciudadana, Economía y Sociedad)

- **200 Estudiantes** (14-18 años, 1° a 4° medio)
- **912 Inscripciones** (estudiantes inscritos en múltiples cursos)
- **97 Tareas** distribuidas en los cursos
- **3,278 Entregas** con calificaciones (escala 1.0-7.0)

---

## 🧪 Verificar Instalación

### 1. Verificar Backend

Abre en el navegador: http://localhost:8000/docs

Deberías ver la documentación Swagger de la API.

### 2. Verificar Frontend

Abre en el navegador: http://localhost:5173

Deberías ver la página de inicio de la plataforma.

### 3. Verificar ML Service

Abre en el navegador: http://localhost:8001/health

Deberías ver: `{"status": "healthy"}`

### 4. Iniciar Sesión

1. Ve a http://localhost:5173/login
2. Usa las credenciales del administrador o profesor
3. Verifica que puedas ver el dashboard correspondiente

---

## 🔄 Reinstalar/Resetear Datos

Si necesitas reinstalar desde cero:

```bash
cd backend

# Asegúrate de tener el venv activado
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Ejecutar el script maestro nuevamente
# Este script borrará todos los datos y recreará todo
python setup_complete_platform.py
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'app'"

Asegúrate de estar en el directorio `backend/` y tener el entorno virtual activado.

### Error: "connection refused" al conectar a PostgreSQL

1. Verifica que PostgreSQL esté corriendo
2. Verifica la URL de conexión en el archivo `.env`
3. Verifica que la base de datos `pai_platform` exista

### Error: "Port already in use"

Si el puerto 8000, 5173 o 8001 está ocupado:
- **Backend (8000):** Cambia el puerto en el comando uvicorn
- **Frontend (5173):** Vite elegirá automáticamente otro puerto
- **ML Service (8001):** Cambia el puerto en `ml-service/main.py`

### Datos no se generan correctamente

1. Verifica que la base de datos esté vacía antes de ejecutar el script
2. Verifica los logs del script para ver errores específicos
3. Asegúrate de que todas las dependencias estén instaladas

---

## 📝 Notas Importantes

1. **Seguridad:** Las contraseñas por defecto son solo para desarrollo. Cambia todas las contraseñas en producción.

2. **Datos Reproducibles:** El script usa seeds fijos para generar los mismos datos en cada ejecución.

3. **Backup:** Antes de ejecutar el script de reinstalación, haz backup de tu base de datos si tienes datos importantes.

4. **Entrenamiento ML:** Después de instalar, necesitas entrenar el modelo ML:
   - Inicia sesión como administrador
   - Ve al Admin Dashboard
   - Haz clic en "Entrenar Modelo ML"

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs de los servicios
2. Verifica que todas las dependencias estén instaladas
3. Verifica las variables de entorno
4. Consulta los issues en el repositorio de GitHub

---

¡Listo! Tu plataforma PAI está completamente instalada y configurada con todos los datos. 🎉



