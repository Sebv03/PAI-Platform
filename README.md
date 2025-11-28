# 🎓 Plataforma PAES PAI - Plataforma Preuniversitaria

Plataforma académica enfocada en la preparación de estudiantes de 1° a 4° medio para la Prueba de Acceso a la Educación Superior (PAES) de Chile.

## 📋 Características Principales

- **Gestión de Cursos PAES**: Profesores pueden crear cursos específicos por asignatura y temática PAES
- **Sistema de Tareas y Entregas**: Gestión completa de tareas, entregas y calificaciones (escala 1.0-7.0)
- **Foro de Comunicados**: Sistema de anuncios y comentarios para cada curso
- **Predicción de Riesgo Académico**: Modelo de Machine Learning para identificar estudiantes en riesgo
- **Perfil del Estudiante**: Cuestionario durante el registro para evaluar factores de riesgo proactivos
- **Dashboard de Administración**: Panel completo para gestión y visualización de predicciones

## 🏗️ Arquitectura

- **Frontend**: React + Vite + Zustand
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **ML Service**: Microservicio independiente para predicciones de ML
- **Base de Datos**: PostgreSQL

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Docker y Docker Compose (para despliegue)

### Desarrollo Local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/Sebv03/PAI-Platform.git
   cd PAI-Platform
   ```

2. **Configurar Base de Datos**:
   ```bash
   # Opción 1: Docker Compose
   docker-compose up -d postgres
   
   # Opción 2: PostgreSQL local
   # Crear base de datos: pai_platform
   ```

3. **Configurar Backend**:
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   
   # Configurar variables de entorno (.env)
   # DATABASE_URL=postgresql://usuario:password@localhost:5432/pai_platform
   # SECRET_KEY=tu_secret_key
   
   # Iniciar backend
   uvicorn app.main:app --reload --port 8000
   ```

4. **Configurar ML Service**:
   ```bash
   cd ml-service
   pip install -r requirements.txt
   
   # Iniciar ML service
   python main.py
   ```

5. **Configurar Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Inicializar Datos**:
   ```bash
   # Crear administrador
   cd backend
   python create_admin.py
   
   # Configurar estructura PAES
   python setup_paes_structure.py
   
   # Poblar datos históricos
   python populate_paes_historical_data.py
   ```

**Para más detalles, consulta [INICIO_LOCAL.md](./INICIO_LOCAL.md)**

## 🌐 Desplegar en Internet (Gratuito)

¿Quieres subir tu plataforma a internet de forma **gratuita**?

### 🚀 Opción Rápida: Render.com

1. **Guía rápida**: [DESPLIEGUE_RAPIDO.md](./DESPLIEGUE_RAPIDO.md) - Despliega en menos de 30 minutos
2. **Guía completa**: [HOSTING_GRATUITO_COMPLETO.txt](./HOSTING_GRATUITO_COMPLETO.txt) - Todas las opciones gratuitas detalladas

### Opciones Disponibles

- ⭐ **Render.com** - La más fácil (recomendada para principiantes)
- 🚂 **Railway.app** - Excelente alternativa sin "sueño"
- ✈️ **Fly.io** - Ideal para microservicios
- ☁️ **Oracle Cloud** - VPS gratuito permanente
- 🔄 **Combinación Vercel + Supabase** - Mejor rendimiento

### Características del Plan Gratuito

- ✅ PostgreSQL incluido
- ✅ SSL automático
- ✅ Deploy automático desde GitHub
- ✅ Todos los servicios configurados

⚠️ **Nota**: Los servicios gratuitos de Render se "duermen" después de 15 min de inactividad. La primera carga toma ~30 segundos.

## 📚 Documentación

- **[INICIO_LOCAL.md](./INICIO_LOCAL.md)**: Guía completa para iniciar los servidores localmente
- **[DESPLIEGUE_RAPIDO.md](./DESPLIEGUE_RAPIDO.md)**: Despliegue rápido y gratuito en Render.com
- **[HOSTING_GRATUITO_COMPLETO.txt](./HOSTING_GRATUITO_COMPLETO.txt)**: Guía completa de todas las opciones de hosting gratuito
- **[GUIA_DESPLIEGUE.md](./GUIA_DESPLIEGUE.md)**: Guía detallada para desplegar en producción (VPS de pago)
- **[GUIA_COLAB_MODELO_COMPLETO.md](./GUIA_COLAB_MODELO_COMPLETO.md)**: Guía para usar el modelo ML en Google Colab
- **[README_DATASET_HISTORICO.md](./README_DATASET_HISTORICO.md)**: Documentación del dataset histórico
- **[CREDENCIALES_PAI.md](./CREDENCIALES_PAI.md)**: Credenciales de acceso de prueba
- **[DOCUMENTACION_COMPLETA_PAI.txt](./DOCUMENTACION_COMPLETA_PAI.txt)**: Documentación técnica completa

## 🎯 Roles y Permisos

- **Administrador**: Gestión completa, entrenar modelo ML, ver todas las predicciones
- **Profesor**: Crear y gestionar cursos, tareas, calificar, ver predicciones de sus cursos
- **Estudiante**: Inscribirse en cursos, entregar tareas, ver calificaciones, participar en foro

## 📊 Modelo de Machine Learning

El sistema utiliza un modelo de Random Forest para predecir el riesgo académico de los estudiantes basándose en:

- **Features Transaccionales**: Tasa de retraso, tasa de no entrega, promedio de notas, variabilidad
- **Features de Perfil**: Motivación, tiempo disponible, horas de sueño, horas de estudio, disfrute del estudio, tranquilidad del lugar de estudio, presión académica, género

## 🔐 Credenciales de Prueba

Ver [CREDENCIALES_PAI.md](./CREDENCIALES_PAI.md) para credenciales de acceso.

## 📦 Estructura del Proyecto

```
PAI-Platform/
├── backend/              # API FastAPI
│   ├── app/             # Código de la aplicación
│   ├── create_admin.py  # Script para crear administrador
│   ├── setup_paes_structure.py  # Configurar estructura PAES
│   └── populate_paes_historical_data.py  # Poblar datos históricos
├── frontend/            # Aplicación React
├── ml-service/          # Microservicio ML
├── datasets/            # Datasets para entrenamiento
└── docker-compose.yml   # Configuración Docker
```

## 🛠️ Scripts Útiles

- `backend/create_admin.py`: Crear usuario administrador
- `backend/setup_paes_structure.py`: Configurar profesores y cursos PAES
- `backend/populate_paes_historical_data.py`: Generar datos históricos
- `export_historical_data_with_profiles.py`: Exportar dataset histórico

## 📄 Licencia

[Agregar licencia aquí]

## 👥 Contribuidores

[Agregar información de contribuidores]

---

**Desarrollado para preparar estudiantes chilenos para la PAES** 🇨🇱



