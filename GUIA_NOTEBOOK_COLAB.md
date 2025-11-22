# 📓 Guía Completa - Notebook de Google Colab para Modelo ML

Esta guía te ayudará a crear y ejecutar el notebook de Google Colab que replica la lógica del modelo ML de la plataforma PAI.

## 🚀 Pasos Rápidos

### Paso 1: Crear el Notebook en Google Colab

1. Ve a [Google Colab](https://colab.research.google.com/)
2. Haz clic en **"Nuevo notebook"**
3. Copia y pega las celdas de abajo (una por una)

---

## 📝 Celdas del Notebook

### Celda 1: Título y Descripción (Markdown)

```markdown
# 🎓 Modelo de Predicción de Riesgo Académico - PAI Platform

Este notebook replica la lógica del modelo ML usado en la plataforma PAI para predecir el riesgo académico de los estudiantes.

## 📋 Contenido

1. Importación de librerías
2. Generación de dataset de prueba
3. Feature Engineering
4. Entrenamiento del modelo
5. Evaluación y visualización de resultados
```

### Celda 2: Instalación de Librerías (Python)

```python
# Instalar librerías necesarias (solo la primera vez)
!pip install pandas numpy scikit-learn matplotlib seaborn -q
```

### Celda 3: Importación de Librerías (Python)

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo de gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Librerías importadas correctamente")
```

### Celda 4: Subir Archivo de Utilidades (Opcional)

Si prefieres usar el archivo `ml_service_colab_utils.py`, súbelo a Colab:

```python
# Opción 1: Subir el archivo desde tu computadora
from google.colab import files
uploaded = files.upload()  # Selecciona ml_service_colab_utils.py

# Opción 2: Copiar el contenido directamente (ver siguiente celda)
```

**O** incluir el código directamente en el notebook (recomendado para Colab):

### Celda 5: Funciones de Generación de Datos (Python)

Copia el contenido completo de `ml_service_colab_utils.py` aquí, o simplemente incluye esta versión simplificada:

```python
# Función para generar datos sintéticos
def generate_synthetic_data(n_students=200, n_courses=10, tasks_per_course=8, random_seed=42):
    """Genera un dataset sintético de estudiantes, cursos, tareas y entregas."""
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    data = []
    base_date = datetime(2024, 1, 15)
    
    # Generar inscripciones de estudiantes en cursos
    enrollments = []
    for student_id in range(1, n_students + 1):
        n_courses_student = np.random.randint(1, 4)
        student_courses = np.random.choice(range(1, n_courses + 1), size=n_courses_student, replace=False)
        
        for course_id in student_courses:
            enrollment_date = base_date + timedelta(days=np.random.randint(-30, 0))
            enrollments.append({
                'student_id': student_id,
                'course_id': course_id,
                'enrollment_date': enrollment_date
            })
    
    # Generar tareas para cada curso
    tasks = []
    for course_id in range(1, n_courses + 1):
        for task_num in range(1, tasks_per_course + 1):
            task_id = (course_id - 1) * tasks_per_course + task_num
            task_created_at = base_date + timedelta(days=(task_num - 1) * 14)
            due_date = task_created_at + timedelta(days=7)
            tasks.append({
                'task_id': task_id,
                'course_id': course_id,
                'task_created_at': task_created_at,
                'due_date': due_date
            })
    
    # Generar datos de entregas
    for enrollment in enrollments:
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        enrollment_date = enrollment['enrollment_date']
        course_tasks = [t for t in tasks if t['course_id'] == course_id]
        
        # Determinar perfil del estudiante (30% alto riesgo, 70% bajo riesgo)
        is_high_risk = np.random.random() < 0.3
        
        for task in course_tasks:
            task_id = task['task_id']
            due_date = task['due_date']
            
            # Probabilidad de entrega basada en perfil de riesgo
            if is_high_risk:
                submission_prob = np.random.uniform(0.3, 0.7)
                late_submission_prob = 0.6
                avg_grade = np.random.uniform(2.5, 4.0)
            else:
                submission_prob = np.random.uniform(0.7, 0.95)
                late_submission_prob = 0.2
                avg_grade = np.random.uniform(4.5, 6.5)
            
            submitted = np.random.random() < submission_prob
            
            if submitted:
                is_late = np.random.random() < late_submission_prob
                if is_late:
                    days_late = np.random.randint(1, 15)
                    submitted_at = due_date + timedelta(days=days_late)
                else:
                    days_early = np.random.randint(-2, 1)
                    submitted_at = due_date + timedelta(days=days_early)
                
                grade_variability = np.random.uniform(0.5, 1.5)
                grade = max(1.0, min(7.0, np.random.normal(avg_grade, grade_variability)))
                grade = round(grade, 2)
                
                submission_id = len([d for d in data if d.get('submission_id')]) + 1
                data.append({
                    'task_id': task_id,
                    'course_id': course_id,
                    'student_id': student_id,
                    'task_created_at': task['task_created_at'],
                    'due_date': due_date,
                    'enrollment_date': enrollment_date,
                    'submission_id': submission_id,
                    'submitted_at': submitted_at,
                    'grade': grade
                })
            else:
                data.append({
                    'task_id': task_id,
                    'course_id': course_id,
                    'student_id': student_id,
                    'task_created_at': task['task_created_at'],
                    'due_date': due_date,
                    'enrollment_date': enrollment_date,
                    'submission_id': None,
                    'submitted_at': None,
                    'grade': None
                })
    
    return pd.DataFrame(data)

print("✅ Función de generación de datos cargada")
```

### Celda 6: Generar Dataset (Python)

```python
# Generar datos
print("🔄 Generando dataset sintético...")
df = generate_synthetic_data(n_students=200, n_courses=10, tasks_per_course=8)

print(f"✅ Dataset generado: {len(df)} registros")
print(f"   - Estudiantes únicos: {df['student_id'].nunique()}")
print(f"   - Cursos únicos: {df['course_id'].nunique()}")
print(f"   - Tareas únicas: {df['task_id'].nunique()}")
print(f"   - Entregas: {df['submission_id'].notna().sum()}")
print(f"   - Sin entregar: {df['submission_id'].isna().sum()}")

# Mostrar primeras filas
df.head(10)
```

### Celda 7: Feature Engineering - Función (Python)

```python
def calculate_features(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula las features para cada estudiante-curso."""
    # Convertir fechas a datetime
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])
    
    # Agrupar por estudiante y curso
    grouped = data.groupby(['student_id', 'course_id'])
    results = []
    
    for (student_id, course_id), group in grouped:
        # 1. Tasa de retraso en entregas
        delay_rate = 0.0
        valid_submissions = group[(group['submitted_at'].notna()) & (group['due_date'].notna())]
        
        if not valid_submissions.empty:
            delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
            late_submissions = (delays > 0).sum()
            total_submissions = len(valid_submissions)
            delay_rate = late_submissions / total_submissions if total_submissions > 0 else 0.0
        else:
            delay_rate = 1.0
        
        # 2. Tasa de no entrega
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique()
        non_submission_rate = 1.0 - (submitted_tasks / total_tasks) if total_tasks > 0 else 1.0
        non_submission_rate = max(0.0, min(1.0, non_submission_rate))
        
        # 3. Promedio de notas (normalizado 0-1)
        grades = group[group['grade'].notna()]['grade']
        if grades.empty:
            average_grade = 0.0
        else:
            average_grade = (grades.mean() - 1.0) / 6.0
        
        # 4. Variabilidad de notas
        if grades.empty or len(grades) < 2:
            grade_variability = 0.0
        else:
            grade_std = grades.std()
            grade_variability = min(grade_std / 3.0, 1.0)
        
        results.append({
            'student_id': student_id,
            'course_id': course_id,
            'submission_delay_rate': delay_rate,
            'non_submission_rate': non_submission_rate,
            'average_grade': average_grade,
            'grade_variability': grade_variability
        })
    
    return pd.DataFrame(results)

print("✅ Función de feature engineering cargada")
```

### Celda 8: Calcular Features (Python)

```python
# Calcular features
print("🔄 Calculando features...")
features_df = calculate_features(df)

print(f"✅ Features calculadas: {len(features_df)} estudiantes-cursos")
print("\n📊 Primeras filas de features:")
features_df.head(10)
```

### Celda 9: Calcular Variable Objetivo (Python)

```python
# Calcular variable objetivo (target)
# Riesgo alto (1) si: promedio < 4.0 (en escala 1-7) o tasa de no entrega > 0.5
def calculate_target(features_df: pd.DataFrame) -> pd.Series:
    """Calcula la variable objetivo (Y) basada en las features."""
    average_grade_original = features_df['average_grade'] * 6.0 + 1.0
    risk_high = ((average_grade_original < 4.0) | (features_df['non_submission_rate'] > 0.5))
    return risk_high.astype(int)

features_df['risk'] = calculate_target(features_df)

print("✅ Variable objetivo calculada")
print(f"\n📊 Distribución de riesgo:")
print(features_df['risk'].value_counts())
```

### Celda 10: Preparar Datos para Entrenamiento (Python)

```python
# Preparar datos para entrenamiento
feature_names = [
    'submission_delay_rate',
    'non_submission_rate',
    'average_grade',
    'grade_variability'
]

X = features_df[feature_names].values
y = features_df['risk'].values

print(f"📊 Datos preparados:")
print(f"   - Features (X): {X.shape}")
print(f"   - Target (y): {y.shape}")
print(f"   - Clases: {np.unique(y, return_counts=True)}")

# Dividir en entrenamiento y prueba
indices = np.arange(len(features_df))
train_indices, test_indices = train_test_split(
    indices,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train, X_test = X[train_indices], X[test_indices]
y_train, y_test = y[train_indices], y[test_indices]

print(f"\n✅ Datos divididos:")
print(f"   - Entrenamiento: {X_train.shape[0]} muestras")
print(f"   - Prueba: {X_test.shape[0]} muestras")
```

### Celda 11: Entrenar Modelo (Python)

```python
# Crear y entrenar el modelo (mismos parámetros que el proyecto)
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)

print("🔄 Entrenando modelo...")
model.fit(X_train, y_train)
print("✅ Modelo entrenado exitosamente")

# Importancia de las features
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n📊 Importancia de Features:")
print(feature_importance)

# Visualizar importancia
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance, x='importance', y='feature', palette='viridis')
plt.title('Importancia de Features en el Modelo', fontsize=14, fontweight='bold')
plt.xlabel('Importancia')
plt.tight_layout()
plt.show()
```

### Celda 12: Evaluar Modelo (Python)

```python
# Hacer predicciones
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Calcular métricas
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print("=" * 60)
print("📊 MÉTRICAS DEL MODELO")
print("=" * 60)
print(f"\n✅ Accuracy:  {accuracy:.4f}")
print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall:    {recall:.4f}")
print(f"✅ F1-Score:  {f1:.4f}")

print("\n" + "=" * 60)
print("📋 REPORTE DE CLASIFICACIÓN")
print("=" * 60)
print(classification_report(y_test, y_pred, target_names=['Riesgo Bajo', 'Riesgo Alto']))
```

### Celda 13: Matriz de Confusión (Python)

```python
# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Riesgo Bajo', 'Riesgo Alto'],
            yticklabels=['Riesgo Bajo', 'Riesgo Alto'])
plt.title('Matriz de Confusión', fontsize=14, fontweight='bold')
plt.ylabel('Real')
plt.xlabel('Predicho')
plt.tight_layout()
plt.show()

# Desglose
tn, fp, fn, tp = cm.ravel()
print("\n📊 Desglose de la Matriz de Confusión:")
print(f"   - Verdaderos Negativos (TN): {tn}")
print(f"   - Falsos Positivos (FP): {fp}")
print(f"   - Falsos Negativos (FN): {fn}")
print(f"   - Verdaderos Positivos (TP): {tp}")
```

### Celda 14: Tabla de Predicciones (Python)

```python
# Crear tabla de predicciones
predictions_df = pd.DataFrame({
    'student_id': features_df.iloc[test_indices]['student_id'].values,
    'course_id': features_df.iloc[test_indices]['course_id'].values,
    'risk_real': y_test,
    'risk_predicted': y_pred,
    'prob_riesgo_bajo': y_pred_proba[:, 0],
    'prob_riesgo_alto': y_pred_proba[:, 1],
    'confidence': np.max(y_pred_proba, axis=1)
})

print("📋 Tabla de Predicciones (primeras 20 filas):")
print(predictions_df.head(20))

# Análisis de aciertos
predictions_df['correct'] = predictions_df['risk_real'] == predictions_df['risk_predicted']
print(f"\n📊 Análisis de Predicciones:")
print(f"   - Predicciones correctas: {predictions_df['correct'].sum()} ({predictions_df['correct'].mean()*100:.1f}%)")
print(f"   - Predicciones incorrectas: {(~predictions_df['correct']).sum()} ({(~predictions_df['correct']).mean()*100:.1f}%)")
```

### Celda 15: Resumen Final (Python)

```python
print("=" * 60)
print("🎯 RESUMEN DEL MODELO")
print("=" * 60)
print(f"\n📊 Dataset:")
print(f"   - Total estudiantes-cursos: {len(features_df)}")
print(f"   - Estudiantes con riesgo alto: {(features_df['risk'] == 1).sum()}")
print(f"   - Estudiantes con riesgo bajo: {(features_df['risk'] == 0).sum()}")

print(f"\n🤖 Modelo:")
print(f"   - Tipo: RandomForestClassifier")
print(f"   - Features: {len(feature_names)}")
print(f"   - Árboles: {model.n_estimators}")
print(f"   - Profundidad máxima: {model.max_depth}")

print(f"\n✅ Métricas:")
print(f"   - Accuracy:  {accuracy:.4f}")
print(f"   - Precision: {precision:.4f}")
print(f"   - Recall:    {recall:.4f}")
print(f"   - F1-Score:  {f1:.4f}")

print(f"\n📈 Features más importantes:")
for idx, row in feature_importance.head().iterrows():
    print(f"   {idx+1}. {row['feature']}: {row['importance']:.4f}")

print("\n" + "=" * 60)
print("✅ Notebook completado exitosamente")
print("=" * 60)
```

---

## 📦 Alternativa: Notebook Completo Pre-hecho

También puedes:

1. **Descargar el archivo completo**: Si tienes acceso al repositorio, puedes descargar el notebook completo
2. **Subirlo a Colab**: Ve a "Archivo" > "Subir notebook" en Colab

---

## ✅ Resultados Esperados

Después de ejecutar todas las celdas, deberías ver:

- ✅ Dataset generado con ~200 estudiantes y 10 cursos
- ✅ 4 features calculadas para cada estudiante-curso
- ✅ Modelo entrenado con métricas:
  - Accuracy: ~0.85-0.95
  - Precision: ~0.85-0.95
  - Recall: ~0.85-0.95
  - F1-Score: ~0.85-0.95
- ✅ Visualizaciones de importancia de features
- ✅ Matriz de confusión
- ✅ Tabla de predicciones con probabilidades

---

## 🔍 Comparación con el Proyecto

Este notebook replica exactamente:

1. ✅ La misma lógica de feature engineering
2. ✅ Los mismos parámetros del modelo (RandomForestClassifier)
3. ✅ La misma definición de variable objetivo (riesgo alto)
4. ✅ Las mismas métricas de evaluación

Los resultados deberían ser similares a los obtenidos en el proyecto local.

---

## 💡 Tips

- Ejecuta las celdas en orden
- Si hay errores, revisa que las librerías estén instaladas
- Puedes ajustar los parámetros de generación de datos (`n_students`, `n_courses`, etc.)
- Los gráficos se mostrarán automáticamente debajo de cada celda

---

**¡Listo! 🎉 Ya tienes tu notebook de Colab funcionando.**

