# 📓 Guía - Notebook de Google Colab con Dataset CSV

Esta guía te muestra cómo usar el notebook de Colab con el CSV generado `test_dataset.csv`.

## 📋 Pasos

### Paso 1: Generar el CSV (Solo una vez)

Si no tienes el CSV, ejecuta localmente:

```bash
python generate_test_dataset.py
```

Esto creará el archivo `datasets/test_dataset.csv` con:
- 200 estudiantes
- 10 cursos
- 80 tareas (8 por curso)
- 3,048 registros totales
- Datos sintéticos realistas

### Paso 2: Abrir Google Colab

1. Ve a [Google Colab](https://colab.research.google.com/)
2. Crea un nuevo notebook
3. Copia y pega las siguientes celdas

---

## 📝 Celdas del Notebook

### Celda 1: Título (Markdown)

```markdown
# 🎓 Modelo de Predicción de Riesgo Académico - PAI Platform

Este notebook replica la lógica del modelo ML usado en la plataforma PAI.

## 📋 Contenido

1. Importación de librerías
2. Cargar dataset CSV
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

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Librerías importadas correctamente")
```

### Celda 4: Cargar Dataset CSV (Python)

**Opción A: Subir archivo manualmente**

```python
# Subir el archivo CSV desde tu computadora
from google.colab import files
uploaded = files.upload()  # Selecciona el archivo test_dataset.csv

# Cargar el CSV
df = pd.read_csv('test_dataset.csv')

print("✅ Dataset cargado exitosamente")
print(f"   - Total registros: {len(df)}")
print(f"   - Estudiantes únicos: {df['student_id'].nunique()}")
print(f"   - Cursos únicos: {df['course_id'].nunique()}")
print(f"   - Entregas: {df['submission_id'].notna().sum()}")
print(f"   - Sin entregar: {df['submission_id'].isna().sum()}")

df.head(10)
```

**Opción B: Cargar desde GitHub (si lo subiste)**

```python
# Reemplaza con la URL real de tu CSV en GitHub
url = "https://raw.githubusercontent.com/Sebv03/PAI-Platform/main/datasets/test_dataset.csv"
df = pd.read_csv(url)

print("✅ Dataset cargado desde GitHub")
print(f"   - Total registros: {len(df)}")
print(f"   - Estudiantes únicos: {df['student_id'].nunique()}")
print(f"   - Cursos únicos: {df['course_id'].nunique()}")

df.head(10)
```

### Celda 5: Feature Engineering - Función (Python)

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
        average_grade = (grades.mean() - 1.0) / 6.0 if not grades.empty else 0.0
        
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

### Celda 6: Calcular Features (Python)

```python
# Calcular features
print("🔄 Calculando features...")
features_df = calculate_features(df)

print(f"✅ Features calculadas: {len(features_df)} estudiantes-cursos")
print("\n📊 Primeras filas de features:")
features_df.head(10)
```

### Celda 7: Calcular Variable Objetivo (Python)

```python
# Calcular variable objetivo (target)
# Riesgo alto (1) si: promedio < 4.0 (en escala 1-7) o tasa de no entrega > 0.5
average_grade_original = features_df['average_grade'] * 6.0 + 1.0
features_df['risk'] = ((average_grade_original < 4.0) | (features_df['non_submission_rate'] > 0.5)).astype(int)

print("✅ Variable objetivo calculada")
print(f"\n📊 Distribución de riesgo:")
print(features_df['risk'].value_counts())
print(f"\n📈 Estadísticas de features por nivel de riesgo:")
features_df.groupby('risk').agg({
    'submission_delay_rate': 'mean',
    'non_submission_rate': 'mean',
    'average_grade': 'mean',
    'grade_variability': 'mean'
}).round(3)
```

### Celda 8: Preparar Datos y Entrenar Modelo (Python)

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

# Entrenar modelo
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)

print("\n🔄 Entrenando modelo...")
model.fit(X_train, y_train)
print("✅ Modelo entrenado exitosamente")

# Importancia de features
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

### Celda 9: Evaluar Modelo (Python)

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

### Celda 10: Matriz de Confusión (Python)

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

### Celda 11: Tabla de Predicciones (Python)

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

predictions_df['correct'] = predictions_df['risk_real'] == predictions_df['risk_predicted']

print("📋 Tabla de Predicciones (primeras 20 filas):")
print(predictions_df.head(20))

print(f"\n📊 Análisis de Predicciones:")
print(f"   - Predicciones correctas: {predictions_df['correct'].sum()} ({predictions_df['correct'].mean()*100:.1f}%)")
print(f"   - Predicciones incorrectas: {(~predictions_df['correct']).sum()} ({(~predictions_df['correct']).mean()*100:.1f}%)")
```

### Celda 12: Resumen Final (Python)

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

## 📦 Archivos Necesarios

1. **`test_dataset.csv`**: Dataset de prueba generado
   - Ubicación: `datasets/test_dataset.csv`
   - Tamaño: ~3,048 registros
   - Formato: CSV con columnas necesarias

2. **Subir a Colab**: Puedes subirlo manualmente o desde GitHub

---

## ✅ Resultados Esperados

Después de ejecutar todas las celdas:

- ✅ Dataset cargado: 3,048 registros
- ✅ Features calculadas: ~300+ estudiantes-cursos
- ✅ Modelo entrenado con métricas:
  - Accuracy: ~0.85-0.95
  - Precision: ~0.85-0.95
  - Recall: ~0.85-0.95
  - F1-Score: ~0.85-0.95
- ✅ Visualizaciones de importancia y matriz de confusión
- ✅ Tabla de predicciones con probabilidades

---

## 🔍 Ventajas de Usar CSV

- ✅ Datos fijos y reproducibles
- ✅ No necesitas generar datos cada vez
- ✅ Puedes compartir el mismo dataset
- ✅ Fácil de subir a Colab
- ✅ Compatible con el proyecto local

---

**¡Listo! 🎉 Ya tienes tu notebook de Colab funcionando con el CSV.**

