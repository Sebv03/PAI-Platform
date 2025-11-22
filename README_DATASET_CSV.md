# 📊 Dataset CSV para Modelo ML

Este documento explica cómo usar el dataset CSV generado para entrenar el modelo ML.

## 📦 Archivo Generado

**Archivo**: `datasets/test_dataset.csv`

**Características**:
- 3,048 registros totales
- 200 estudiantes únicos
- 10 cursos únicos
- 80 tareas (8 por curso)
- 74% tasa de entrega
- Notas en escala 1-7

## 🚀 Cómo Generar el CSV

Ejecuta el script desde la raíz del proyecto:

```bash
python generate_test_dataset.py
```

Esto creará el archivo `datasets/test_dataset.csv`.

## 📋 Estructura del CSV

El CSV contiene las siguientes columnas:

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

1. **Subir el CSV a Colab**:
   ```python
   from google.colab import files
   uploaded = files.upload()  # Selecciona test_dataset.csv
   df = pd.read_csv('test_dataset.csv')
   ```

2. **O cargar desde GitHub**:
   ```python
   url = "https://raw.githubusercontent.com/Sebv03/PAI-Platform/main/datasets/test_dataset.csv"
   df = pd.read_csv(url)
   ```

3. **Seguir la guía**: `GUIA_COLAB_CON_CSV.md`

## 📈 Datos Generados

### Perfiles de Estudiantes

- **70% Bajo Riesgo**: 
  - Alta tasa de entrega (70-95%)
  - Pocas entregas tardías (20%)
  - Notas promedio: 4.5-6.5

- **30% Alto Riesgo**:
  - Baja tasa de entrega (30-70%)
  - Muchas entregas tardías (60%)
  - Notas promedio: 2.5-4.0

### Variable Objetivo

Riesgo alto (1) si:
- Promedio de notas < 4.0 (en escala 1-7), **O**
- Tasa de no entrega > 0.5

## ✅ Validación

El CSV está listo para usar directamente con:

1. ✅ Feature engineering del proyecto
2. ✅ Entrenamiento del modelo RandomForestClassifier
3. ✅ Evaluación de métricas

## 🔄 Regenerar el Dataset

Si necesitas regenerar el dataset con diferentes parámetros:

1. Edita `generate_test_dataset.py`
2. Modifica los parámetros:
   ```python
   df = generate_synthetic_data(
       n_students=300,      # Más estudiantes
       n_courses=15,        # Más cursos
       tasks_per_course=10, # Más tareas por curso
       random_seed=42       # Misma semilla = mismos datos
   )
   ```
3. Ejecuta: `python generate_test_dataset.py`

## 📝 Notas

- El dataset usa `random_seed=42` para reproducibilidad
- Las fechas están en formato ISO (YYYY-MM-DD)
- Los valores NaN representan datos faltantes (no entregado, no calificado)
- El CSV está codificado en UTF-8

## 🎯 Resultados Esperados

Con este dataset, el modelo debería alcanzar:

- **Accuracy**: ~0.85-0.95
- **Precision**: ~0.85-0.95
- **Recall**: ~0.85-0.95
- **F1-Score**: ~0.85-0.95

Estos resultados son similares a los obtenidos con datos históricos reales del proyecto.

---

**¡Listo! 🎉 El CSV está preparado para usar en Colab o en el proyecto local.**

