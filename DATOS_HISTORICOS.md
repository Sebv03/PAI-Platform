# Datos Históricos Generados

Este documento describe los datos históricos que se han generado en la base de datos para entrenar el modelo de Machine Learning.

## Resumen de Datos Creados

- **29 Usuarios**:
  - 4 Docentes
  - 25 Estudiantes

- **4 Cursos**:
  - Programación I
  - Base de Datos
  - Estructuras de Datos
  - Ingeniería de Software

- **70 Inscripciones**: Estudiantes inscritos en cursos (15-20 estudiantes por curso)

- **20 Tareas**: 5 tareas por curso, distribuidas a lo largo de 3 meses

- **245 Entregas**: Con diferentes patrones de comportamiento:
  - ~70% de entregas realizadas
  - ~30% de tareas no entregadas
  - ~35% de entregas con retraso (1-7 días)

- **245 Calificaciones**: Asignadas a las entregas con notas entre 1.0 y 7.0

- **9 Comunicados**: Anuncios en los cursos

## Patrones de Datos Generados

### Comportamiento de Estudiantes

Los datos simulan diferentes perfiles de estudiantes:

1. **Estudiantes de Alto Rendimiento**:
   - Entregan todas las tareas a tiempo
   - Calificaciones promedio: 5.5 - 7.0

2. **Estudiantes de Rendimiento Medio**:
   - Entregan la mayoría de tareas, algunas con retraso
   - Calificaciones promedio: 4.0 - 5.5

3. **Estudiantes en Riesgo**:
   - Entregan pocas tareas o con retrasos frecuentes
   - Calificaciones promedio: 1.0 - 4.0

### Calificaciones

- Las calificaciones están correlacionadas con el comportamiento:
  - Entregas a tiempo: mejor calificación base
  - Entregas con retraso: penalización de 0.2 puntos por día de retraso
  - Rango de notas: 1.0 a 7.0

## Credenciales de Acceso

### Docentes

1. **Roberto Vergara**
   - Email: `roberto.vergara@docente.cl`
   - Password: `password123`

2. **Patricia Méndez**
   - Email: `patricia.mendez@docente.cl`
   - Password: `password123`

3. **Carlos Fernández**
   - Email: `carlos.fernandez@docente.cl`
   - Password: `password123`

4. **María Vega**
   - Email: `maria.vega@docente.cl`
   - Password: `password123`

### Estudiantes (Ejemplos)

Todos los estudiantes tienen la contraseña: `password123`

- `juan.perez@estudiante.cl`
- `maria.gonzalez@estudiante.cl`
- `carlos.rodriguez@estudiante.cl`
- `ana.martinez@estudiante.cl`
- ... (ver el script para la lista completa)

## Features para ML Disponibles

Con estos datos históricos, puedes calcular las siguientes features:

1. **Tasa de Retraso en Entregas**: ✅ Disponible
   - Comparar `submissions.submitted_at` con `tasks.due_date`

2. **Tasa de No Entrega**: ✅ Disponible
   - Comparar tareas asignadas vs entregas realizadas

3. **Promedio de Notas**: ✅ Disponible
   - `AVG(submissions.grade)` por estudiante por curso

4. **Variabilidad de Notas**: ✅ Disponible
   - `STDDEV(submissions.grade)` por estudiante por curso

## Variable Objetivo (Y)

Para definir la variable objetivo, puedes usar:

```sql
-- Ejemplo de cálculo de Y por estudiante por curso
SELECT 
    student_id,
    course_id,
    AVG(grade) as avg_grade,
    CASE 
        WHEN AVG(grade) < 4.0 THEN 1  -- Riesgo Alto
        ELSE 0  -- Riesgo Bajo
    END as risk_label
FROM submissions s
JOIN tasks t ON s.task_id = t.id
WHERE grade IS NOT NULL
GROUP BY student_id, course_id;
```

## Ejecutar el Script

Para regenerar los datos históricos:

```bash
cd backend
python populate_historical_data.py
```

**Nota**: El script verifica si los usuarios ya existen antes de crearlos, por lo que puedes ejecutarlo múltiples veces sin duplicar datos.


