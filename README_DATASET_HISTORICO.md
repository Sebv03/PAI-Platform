# 📊 Dataset Histórico de la Plataforma

Este documento explica cómo obtener y usar el dataset histórico real que usa la plataforma PAI para entrenar el modelo ML.

## 📦 Archivo Exportado

**Archivo**: `datasets/historical_dataset.csv`

**Características**:
- Datos reales de la base de datos de la plataforma
- Misma estructura que usa el ML service
- Misma query que ejecuta el modelo para entrenar
- Datos históricos generados por `populate_historical_data.py`

## 🚀 Cómo Exportar el Dataset

Ejecuta el script desde la raíz del proyecto:

```bash
python export_historical_data_to_csv.py
```

**Requisitos**:
- La base de datos debe estar corriendo
- Debe tener datos históricos (ejecutar `populate_historical_data.py` primero)
- Debe tener acceso a la base de datos configurada en `backend/app/core/config.py`

## 📋 Estructura del CSV

El CSV contiene las mismas columnas que usa el ML service:

| Columna | Descripción | Tipo |
|---------|-------------|------|
| `task_id` | ID de la tarea | int |
| `course_id` | ID del curso | int |
| `student_id` | ID del estudiante | int |
| `task_created_at` | Fecha de creación de la tarea | datetime |
| `due_date` | Fecha límite de entrega | datetime |
| `enrollment_date` | Fecha de inscripción del estudiante | datetime |
| `submission_id` | ID de la entrega (NaN si no entregó) | float/NaN |
| `submitted_at` | Fecha de entrega (NaN si no entregó) | datetime/NaN |
| `grade` | Nota recibida (NaN si no entregó o no calificado) | float/NaN |

## 🎓 Uso en Google Colab

1. **Exportar el CSV** (desde tu máquina local):
   ```bash
   python export_historical_data_to_csv.py
   ```

2. **Subir el CSV a Colab**:
   ```python
   from google.colab import files
   uploaded = files.upload()  # Selecciona historical_dataset.csv
   df = pd.read_csv('historical_dataset.csv')
   ```

3. **O cargar desde GitHub** (si lo subiste):
   ```python
   url = "https://raw.githubusercontent.com/Sebv03/PAI-Platform/main/datasets/historical_dataset.csv"
   df = pd.read_csv(url)
   ```

4. **Seguir la guía**: `GUIA_COLAB_CON_CSV.md` (usa `historical_dataset.csv` en lugar de `test_dataset.csv`)

## 📈 Datos del Dataset

### Estadísticas Actuales

- **Total registros**: ~351 (varía según datos en BD)
- **Estudiantes únicos**: ~26
- **Cursos únicos**: ~5
- **Tareas únicas**: ~21
- **Tasa de entrega**: ~70%
- **Notas promedio**: ~4.75 (escala 1-7)

### Origen de los Datos

Los datos provienen de:
- Usuarios creados por `populate_historical_data.py`
- Cursos: Programación I, Base de Datos, Estructuras de Datos, Ingeniería de Software
- Tareas distribuidas a lo largo del semestre
- Entregas con diferentes patrones de comportamiento
- Calificaciones basadas en rendimiento y puntualidad

## ✅ Validación

Este CSV es **exactamente** el mismo que usa:

1. ✅ El ML service para entrenar el modelo (`data_service.py`)
2. ✅ La misma query SQL que ejecuta el backend
3. ✅ Los mismos datos que verías en la plataforma

## 🔄 Actualizar el Dataset

Si agregas más datos a la plataforma:

1. Ejecuta `export_historical_data_to_csv.py` nuevamente
2. El CSV se actualizará con los nuevos datos
3. Puedes reentrenar el modelo con los datos actualizados

## 📝 Comparación con Test Dataset

| Característica | Historical Dataset | Test Dataset |
|----------------|-------------------|--------------|
| Origen | Base de datos real | Generado sintéticamente |
| Registros | ~351 | ~3,048 |
| Estudiantes | ~26 | 200 |
| Cursos | ~5 | 10 |
| Uso | Producción/Entrenamiento real | Pruebas/Desarrollo |
| Reproducibilidad | Depende de BD | Fija (seed=42) |

## 🎯 Resultados Esperados

Con este dataset histórico, el modelo debería alcanzar métricas similares a las que obtienes en la plataforma local, ya que son los mismos datos.

## ⚠️ Notas Importantes

- El dataset puede variar si agregas/eliminas datos en la BD
- Las fechas están en formato UTC con timezone
- Los valores NaN representan datos faltantes (no entregado, no calificado)
- El CSV está codificado en UTF-8

## 🔍 Query SQL Usada

El script usa la misma query que el ML service:

```sql
SELECT 
    t.id as task_id,
    t.course_id,
    t.due_date,
    t.created_at as task_created_at,
    e.student_id,
    e.enrollment_date,
    s.id as submission_id,
    s.submitted_at,
    s.grade
FROM tasks t
INNER JOIN enrollments e ON t.course_id = e.course_id
LEFT JOIN submissions s ON s.task_id = t.id AND s.student_id = e.student_id
ORDER BY e.student_id, t.course_id, t.due_date
```

---

**¡Listo! 🎉 Ahora tienes el mismo dataset que usa la plataforma para entrenar el modelo.**

