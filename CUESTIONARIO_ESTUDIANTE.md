# 📋 Cuestionario de Perfil Estudiantil - Documentación

## 📝 Resumen

Se ha implementado un cuestionario de perfil estudiantil que se completa durante el registro. Este cuestionario proporciona **features predictivas** para el modelo ML, permitiendo evaluar el riesgo académico **antes** de que el estudiante comience a tener problemas, a diferencia del modelo anterior que era reactivo.

## 🎯 Objetivo

Transformar el modelo ML de **reactivo** (detecta riesgo cuando ya hay problemas) a **predictivo** (predice riesgo al inicio del curso basándose en factores de riesgo precursores).

## 📊 Variables del Cuestionario

Todas las variables usan una escala de **1 a 10**:

1. **Motivación** (`motivation`)
   - Qué tan motivado está el estudiante para estudiar
   - 1 = Poco motivado, 10 = Muy motivado

2. **Tiempo Disponible** (`available_time`)
   - Cuánto tiempo disponible tiene para estudiar
   - 1 = Muy poco tiempo, 10 = Mucho tiempo

3. **Horas de Sueño** (`sleep_hours`)
   - Horas de sueño por noche en promedio
   - 1 = Menos de 5 horas, 10 = Más de 8 horas

4. **Horas de Estudio** (`study_hours`)
   - Horas dedicadas a estudiar por semana
   - 1 = Menos de 5 horas, 10 = Más de 20 horas

5. **Gusto por Estudiar** (`enjoyment_studying`)
   - Qué tanto le gusta estudiar
   - 1 = No me gusta, 10 = Me encanta

6. **Tranquilidad del Lugar de Estudio** (`study_place_tranquility`)
   - Qué tan tranquilo es el lugar donde estudia
   - 1 = Muy ruidoso/distracciones, 10 = Muy tranquilo/concentración

7. **Presión Académica** (`academic_pressure`)
   - Qué tanta presión siente por los estudios
   - 1 = Nada de presión, 10 = Mucha presión

8. **Género** (`gender`)
   - Variable categórica: Masculino, Femenino, Otro

## 🗄️ Base de Datos

### Tabla: `student_profiles`

```sql
CREATE TABLE student_profiles (
    id SERIAL PRIMARY KEY,
    student_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    motivation FLOAT NOT NULL CHECK (motivation >= 1 AND motivation <= 10),
    available_time FLOAT NOT NULL CHECK (available_time >= 1 AND available_time <= 10),
    sleep_hours FLOAT NOT NULL CHECK (sleep_hours >= 1 AND sleep_hours <= 10),
    study_hours FLOAT NOT NULL CHECK (study_hours >= 1 AND study_hours <= 10),
    enjoyment_studying FLOAT NOT NULL CHECK (enjoyment_studying >= 1 AND enjoyment_studying <= 10),
    study_place_tranquility FLOAT NOT NULL CHECK (study_place_tranquility >= 1 AND study_place_tranquility <= 10),
    academic_pressure FLOAT NOT NULL CHECK (academic_pressure >= 1 AND academic_pressure <= 10),
    gender VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔌 API Endpoints

### Crear/Actualizar Perfil
```
POST /api/v1/student-profiles/
PUT /api/v1/student-profiles/me
```

**Request Body:**
```json
{
    "motivation": 7.5,
    "available_time": 6.0,
    "sleep_hours": 7.0,
    "study_hours": 8.0,
    "enjoyment_studying": 7.5,
    "study_place_tranquility": 8.0,
    "academic_pressure": 6.5,
    "gender": "femenino"
}
```

### Obtener Mi Perfil
```
GET /api/v1/student-profiles/me
```

### Obtener Perfil de un Estudiante (Admin/Docente)
```
GET /api/v1/student-profiles/student/{student_id}
```

## 🤖 Integración con Modelo ML

### Features Predictivas (Del Cuestionario)

Estas features están disponibles **desde el inicio del curso**:

- `motivation` (normalizado 0-1)
- `available_time` (normalizado 0-1)
- `sleep_hours` (normalizado 0-1)
- `study_hours` (normalizado 0-1)
- `enjoyment_studying` (normalizado 0-1)
- `study_place_tranquility` (normalizado 0-1)
- `academic_pressure` (normalizado 0-1)
- `gender_encoded` (0, 0.5, 1)

### Features Transaccionales (Durante el Curso)

Estas features se completan con valores por defecto si no hay datos:

- `submission_delay_rate` (0-1)
- `non_submission_rate` (0-1)
- `average_grade` (normalizado 0-1)
- `grade_variability` (normalizado 0-1)

### Ventajas del Nuevo Modelo

1. **Predicción Temprana**: Puede predecir riesgo antes de que haya entregas
2. **Menos Dependencia de Datos Transaccionales**: Las features predictivas son suficientes para una evaluación inicial
3. **Factores de Riesgo Precursores**: Identifica problemas potenciales basándose en factores de riesgo conocidos

## 🔄 Flujo de Registro

1. Usuario completa registro básico (email, contraseña, nombre, rol)
2. Si es estudiante, se muestra el cuestionario de perfil
3. Estudiante completa el cuestionario (8 preguntas)
4. Se guarda el perfil en la base de datos
5. El usuario es autenticado y redirigido al dashboard

## 📝 Crear Tabla en Base de Datos

Ejecuta el script de migración:

```bash
cd backend
python add_student_profile_table.py
```

O las tablas se crearán automáticamente al iniciar el servidor si `create_tables()` está activo.

## 🧪 Testing

### Crear Perfil de Estudiante

```bash
# Registrar estudiante y completar cuestionario
POST /api/v1/student-profiles/
Authorization: Bearer <token>
Content-Type: application/json

{
    "motivation": 8,
    "available_time": 7,
    "sleep_hours": 8,
    "study_hours": 7,
    "enjoyment_studying": 8,
    "study_place_tranquility": 9,
    "academic_pressure": 5,
    "gender": "masculino"
}
```

### Obtener Perfil

```bash
GET /api/v1/student-profiles/me
Authorization: Bearer <token>
```

## 📊 Impacto en el Modelo ML

### Antes
- Modelo reactivo: Solo funcionaba después de entregas
- Dependía completamente de datos transaccionales
- No podía predecir riesgo al inicio del curso

### Después
- Modelo predictivo: Funciona desde el inicio
- Features predictivas disponibles inmediatamente
- Puede identificar factores de riesgo precursores
- Features transaccionales se agregan cuando hay datos

## 🚀 Próximos Pasos

1. Reentrenar el modelo ML con las nuevas features
2. Actualizar el Admin Dashboard para mostrar predicciones tempranas
3. Implementar alertas para estudiantes con riesgo alto al inicio
4. Ajustar los pesos de las features según importancia

