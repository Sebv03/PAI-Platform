# 🚀 Guía: Demostración del Modelo ML en Google Colab

Esta guía te muestra cómo entrenar y usar el modelo de predicción de riesgo académico en Google Colab con el dataset histórico completo que incluye perfiles de estudiantes.

## 📋 Requisitos Previos

1. **Dataset CSV**: `historical_dataset_with_profiles.csv`
2. **Google Colab**: Acceso a [Google Colab](https://colab.research.google.com/)
3. **Conexión a internet**: Para descargar librerías

## 📦 Paso 1: Subir el Dataset

1. Abre Google Colab: [https://colab.research.google.com/](https://colab.research.google.com/)
2. Crea un nuevo notebook
3. En la barra lateral izquierda, haz clic en el icono de 📁 (Files)
4. Sube el archivo `historical_dataset_with_profiles.csv` que generaste con el script

**O usar desde GitHub/GDrive:**
```python
# Opción 1: Desde Google Drive (si subiste el archivo ahí)
from google.colab import drive
drive.mount('/content/drive')
df = pd.read_csv('/content/drive/MyDrive/historical_dataset_with_profiles.csv')

# Opción 2: Desde URL (si subiste a GitHub o servidor)
import pandas as pd
url = "URL_DEL_CSV_AQUI"
df = pd.read_csv(url)
```

## 📚 Paso 2: Instalar Librerías

Ejecuta esta celda para instalar las librerías necesarias:

```python
!pip install pandas numpy scikit-learn matplotlib seaborn
```

## 📊 Paso 3: Cargar y Explorar los Datos

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

# Configuración de visualización
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
%matplotlib inline

# Cargar datos
df = pd.read_csv('historical_dataset_with_profiles.csv')

print("=" * 60)
print("DATASET HISTORICO CON PERFILES")
print("=" * 60)
print(f"Total de registros: {len(df)}")
print(f"Estudiantes únicos: {df['student_id'].nunique()}")
print(f"Cursos únicos: {df['course_id'].nunique()}")
print(f"Tareas únicas: {df['task_id'].nunique()}")
print()

print("Columnas del dataset:")
print(df.columns.tolist())
print()

print("Primeras filas del dataset:")
print(df.head())
print()

print("Información del dataset:")
print(df.info())
print()

print("Estadísticas descriptivas:")
print(df.describe())
```

## 🔧 Paso 4: Feature Engineering

Esta celda implementa exactamente la misma lógica que usa la plataforma:

```python
def normalize_profile_features(value, default=5.0):
    """Normaliza features del perfil (escala 1-10) a 0-1"""
    if pd.isna(value):
        return (default - 1.0) / 9.0
    return (value - 1.0) / 9.0

def encode_gender(gender_value):
    """Codifica género: masculino=0, femenino=1, otro=0.5"""
    if pd.isna(gender_value) or gender_value == '':
        return 0.5
    gender_str = str(gender_value).lower()
    if 'femenino' in gender_str or 'mujer' in gender_str or 'female' in gender_str:
        return 1.0
    elif 'masculino' in gender_str or 'hombre' in gender_str or 'male' in gender_str:
        return 0.0
    else:
        return 0.5

def calculate_features(df):
    """
    Calcula las features para cada estudiante-curso.
    Igual que el feature_engineering.py de la plataforma.
    """
    # Convertir fechas a datetime
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    results = []
    
    # Agrupar por estudiante y curso
    for (student_id, course_id), group in df.groupby(['student_id', 'course_id']):
        first_row = group.iloc[0]
        
        # ===== FEATURES DEL PERFIL (Predictivas) =====
        motivation = normalize_profile_features(first_row.get('motivation'))
        available_time = normalize_profile_features(first_row.get('available_time'))
        sleep_hours = normalize_profile_features(first_row.get('sleep_hours'))
        study_hours = normalize_profile_features(first_row.get('study_hours'))
        enjoyment_studying = normalize_profile_features(first_row.get('enjoyment_studying'))
        study_place_tranquility = normalize_profile_features(first_row.get('study_place_tranquility'))
        academic_pressure = normalize_profile_features(first_row.get('academic_pressure'))
        gender_encoded = encode_gender(first_row.get('gender'))
        
        # ===== FEATURES TRANSACCIONALES =====
        # 1. Tasa de retraso en entregas
        valid_submissions = group[
            (group['submitted_at'].notna()) & 
            (group['due_date'].notna())
        ]
        
        if not valid_submissions.empty:
            delays = (valid_submissions['submitted_at'] - valid_submissions['due_date']).dt.total_seconds() / 86400
            late_submissions = (delays > 0).sum()
            delay_rate = late_submissions / len(valid_submissions) if len(valid_submissions) > 0 else 0.5
        else:
            delay_rate = 0.5  # Valor por defecto
        
        # 2. Tasa de no entrega
        total_tasks = len(group['task_id'].unique())
        submitted_tasks = group[group['submission_id'].notna()]['task_id'].nunique() if 'submission_id' in group.columns else 0
        non_submission_rate = 1.0 - (submitted_tasks / total_tasks) if total_tasks > 0 else 0.5
        non_submission_rate = max(0.0, min(1.0, non_submission_rate))
        
        # 3. Promedio de notas (normalizado)
        grades = group[group['grade'].notna()]['grade']
        if not grades.empty:
            avg = grades.mean()
            average_grade = (avg - 1.0) / 6.0  # Normalizar a 0-1 (escala 1-7)
            average_grade = max(0.0, min(1.0, average_grade))
        else:
            average_grade = 0.5  # Valor por defecto
        
        # 4. Variabilidad de notas
        if not grades.empty and len(grades) >= 2:
            grade_std = grades.std()
            grade_variability = min(grade_std / 3.0, 1.0)
        else:
            grade_variability = 0.5  # Valor por defecto
        
        results.append({
            'student_id': student_id,
            'course_id': course_id,
            # Features predictivas (del cuestionario)
            'motivation': motivation,
            'available_time': available_time,
            'sleep_hours': sleep_hours,
            'study_hours': study_hours,
            'enjoyment_studying': enjoyment_studying,
            'study_place_tranquility': study_place_tranquility,
            'academic_pressure': academic_pressure,
            'gender_encoded': gender_encoded,
            # Features transaccionales
            'submission_delay_rate': delay_rate,
            'non_submission_rate': non_submission_rate,
            'average_grade': average_grade,
            'grade_variability': grade_variability
        })
    
    return pd.DataFrame(results)

# Calcular features
print("Calculando features...")
features_df = calculate_features(df)

print(f"[OK] Features calculadas: {len(features_df)} estudiantes-cursos")
print(f"\nFeatures generadas: {', '.join([col for col in features_df.columns if col not in ['student_id', 'course_id']])}")
print()

print("Estadísticas de las features:")
print(features_df.describe())
print()

print("Primeras filas de features:")
print(features_df.head())
```

## 🎯 Paso 5: Calcular Variable Objetivo (Target)

```python
def calculate_target(features_df):
    """
    Calcula la variable objetivo (riesgo alto = 1, riesgo bajo = 0).
    Igual que feature_engineering.py de la plataforma.
    """
    # Desnormalizar average_grade para comparar con 4.0
    average_grade_original = features_df['average_grade'] * 6.0 + 1.0
    
    # Definir riesgo alto basado en datos transaccionales
    if 'average_grade' in features_df.columns and features_df['average_grade'].notna().any():
        risk_high = (
            (average_grade_original < 4.0) | 
            (features_df['non_submission_rate'] > 0.5)
        )
    else:
        # Si no hay datos transaccionales, usar features predictivas
        risk_high = pd.Series([False] * len(features_df), index=features_df.index)
        
        if 'motivation' in features_df.columns:
            risk_high = risk_high | (features_df['motivation'] < 0.3)
        
        if 'academic_pressure' in features_df.columns:
            risk_high = risk_high | (features_df['academic_pressure'] > 0.7)
        
        if 'available_time' in features_df.columns:
            risk_high = risk_high | (features_df['available_time'] < 0.3)
        
        if 'sleep_hours' in features_df.columns:
            risk_high = risk_high | (features_df['sleep_hours'] < 0.3)
    
    return risk_high.astype(int)

# Calcular target
features_df['risk'] = calculate_target(features_df)

print("Distribución del riesgo:")
print(features_df['risk'].value_counts())
print(f"\nPorcentaje de riesgo alto: {features_df['risk'].mean() * 100:.2f}%")
print()
```

## 🔍 Paso 6: Visualización de las Features

```python
# Features para visualizar (sin IDs)
feature_cols = [col for col in features_df.columns if col not in ['student_id', 'course_id', 'risk']]

# Crear subplots
fig, axes = plt.subplots(3, 4, figsize=(16, 12))
axes = axes.flatten()

for i, feature in enumerate(feature_cols):
    ax = axes[i]
    features_df.boxplot(column=feature, by='risk', ax=ax)
    ax.set_title(f'{feature} por Riesgo')
    ax.set_xlabel('Riesgo (0=Bajo, 1=Alto)')
    ax.set_ylabel('Valor Normalizado')

plt.tight_layout()
plt.suptitle('Distribución de Features por Nivel de Riesgo', y=1.02, fontsize=16)
plt.show()

# Matriz de correlación
plt.figure(figsize=(12, 10))
correlation_matrix = features_df[feature_cols].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Matriz de Correlación entre Features')
plt.tight_layout()
plt.show()
```

## 🤖 Paso 7: Entrenar el Modelo

```python
# Features para el modelo
feature_names = [
    'motivation', 'available_time', 'sleep_hours', 'study_hours',
    'enjoyment_studying', 'study_place_tranquility', 'academic_pressure',
    'gender_encoded', 'submission_delay_rate', 'non_submission_rate',
    'average_grade', 'grade_variability'
]

# Preparar datos
X = features_df[feature_names].values
y = features_df['risk'].values

print(f"Total de muestras: {len(X)}")
print(f"Features: {len(feature_names)}")
print(f"Distribución de clases: {np.bincount(y)}")
print()

# Dividir en entrenamiento y prueba (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
)

print(f"Conjunto de entrenamiento: {len(X_train)} muestras")
print(f"Conjunto de prueba: {len(X_test)} muestras")
print()

# Crear y entrenar modelo (RandomForest igual que la plataforma)
print("Entrenando modelo RandomForest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)

model.fit(X_train, y_train)
print("[OK] Modelo entrenado")
print()

# Predicciones
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Métricas
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print("=" * 60)
print("METRICAS DEL MODELO")
print("=" * 60)
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1-Score:  {f1:.3f}")
print()

print("Reporte de Clasificación:")
print(classification_report(y_test, y_pred, target_names=['Riesgo Bajo', 'Riesgo Alto']))
print()

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Riesgo Bajo', 'Riesgo Alto'],
            yticklabels=['Riesgo Bajo', 'Riesgo Alto'])
plt.title('Matriz de Confusión')
plt.ylabel('Real')
plt.xlabel('Predicho')
plt.show()
```

## 📈 Paso 8: Importancia de Features

```python
# Importancia de features
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("Importancia de Features:")
print(feature_importance)
print()

# Visualizar importancia
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance, x='importance', y='feature', palette='viridis')
plt.title('Importancia de Features en el Modelo')
plt.xlabel('Importancia')
plt.tight_layout()
plt.show()
```

## 🔮 Paso 9: Predicciones para Estudiantes Nuevos

```python
def predict_student_risk(profile_features, transactional_features=None):
    """
    Predice el riesgo para un estudiante nuevo.
    
    Args:
        profile_features: dict con features del cuestionario
            - motivation (1-10)
            - available_time (1-10)
            - sleep_hours (1-10)
            - study_hours (1-10)
            - enjoyment_studying (1-10)
            - study_place_tranquility (1-10)
            - academic_pressure (1-10)
            - gender ('masculino', 'femenino', 'otro')
        
        transactional_features: dict opcional con features transaccionales
            Si es None, se usan valores por defecto (0.5)
    """
    # Normalizar features del perfil
    features = [
        normalize_profile_features(profile_features.get('motivation', 5)),
        normalize_profile_features(profile_features.get('available_time', 5)),
        normalize_profile_features(profile_features.get('sleep_hours', 5)),
        normalize_profile_features(profile_features.get('study_hours', 5)),
        normalize_profile_features(profile_features.get('enjoyment_studying', 5)),
        normalize_profile_features(profile_features.get('study_place_tranquility', 5)),
        normalize_profile_features(profile_features.get('academic_pressure', 5)),
        encode_gender(profile_features.get('gender', ''))
    ]
    
    # Features transaccionales (por defecto si no hay datos)
    if transactional_features is None:
        features.extend([0.5, 0.5, 0.5, 0.5])  # Valores por defecto
    else:
        features.extend([
            transactional_features.get('submission_delay_rate', 0.5),
            transactional_features.get('non_submission_rate', 0.5),
            transactional_features.get('average_grade', 0.5),
            transactional_features.get('grade_variability', 0.5)
        ])
    
    # Predecir
    X = np.array(features).reshape(1, -1)
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    
    return {
        'risk': 'Alto' if prediction == 1 else 'Bajo',
        'probability_low': probabilities[0],
        'probability_high': probabilities[1],
        'confidence': max(probabilities)
    }

# Ejemplo 1: Estudiante con alto riesgo (baja motivación, alta presión)
student_high_risk = {
    'motivation': 3,
    'available_time': 3,
    'sleep_hours': 4,
    'study_hours': 3,
    'enjoyment_studying': 2,
    'study_place_tranquility': 5,
    'academic_pressure': 9,
    'gender': 'femenino'
}

result = predict_student_risk(student_high_risk)
print("Ejemplo 1: Estudiante con perfil de alto riesgo")
print(f"Predicción: {result['risk']}")
print(f"Probabilidad de riesgo bajo: {result['probability_low']:.3f}")
print(f"Probabilidad de riesgo alto: {result['probability_high']:.3f}")
print(f"Confianza: {result['confidence']:.3f}")
print()

# Ejemplo 2: Estudiante con bajo riesgo (alta motivación, buena organización)
student_low_risk = {
    'motivation': 8,
    'available_time': 7,
    'sleep_hours': 8,
    'study_hours': 7,
    'enjoyment_studying': 8,
    'study_place_tranquility': 9,
    'academic_pressure': 4,
    'gender': 'masculino'
}

result = predict_student_risk(student_low_risk)
print("Ejemplo 2: Estudiante con perfil de bajo riesgo")
print(f"Predicción: {result['risk']}")
print(f"Probabilidad de riesgo bajo: {result['probability_low']:.3f}")
print(f"Probabilidad de riesgo alto: {result['probability_high']:.3f}")
print(f"Confianza: {result['confidence']:.3f}")
print()
```

## 🎨 Paso 10: Visualizaciones Adicionales

```python
# Distribución de riesgo por género
if 'gender' in df.columns:
    gender_risk = features_df.merge(
        df[['student_id', 'gender']].drop_duplicates(),
        on='student_id'
    )
    
    plt.figure(figsize=(10, 6))
    sns.countplot(data=gender_risk, x='gender', hue='risk', palette='Set2')
    plt.title('Distribución de Riesgo por Género')
    plt.xlabel('Género')
    plt.ylabel('Cantidad')
    plt.legend(title='Riesgo', labels=['Bajo', 'Alto'])
    plt.tight_layout()
    plt.show()

# Scatter plot: Motivación vs Presión Académica
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    features_df['motivation'],
    features_df['academic_pressure'],
    c=features_df['risk'],
    cmap='RdYlGn',
    alpha=0.6,
    s=100
)
plt.colorbar(scatter, label='Riesgo (0=Bajo, 1=Alto)')
plt.xlabel('Motivación (normalizada)')
plt.ylabel('Presión Académica (normalizada)')
plt.title('Motivación vs Presión Académica')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## ✅ Resumen

Este notebook demuestra:
1. ✅ Carga del dataset histórico con perfiles
2. ✅ Feature engineering (igual que la plataforma)
3. ✅ Cálculo de variable objetivo
4. ✅ Entrenamiento del modelo RandomForest
5. ✅ Evaluación con métricas completas
6. ✅ Visualización de importancia de features
7. ✅ Predicciones para estudiantes nuevos
8. ✅ Análisis exploratorio de datos

## 📝 Notas Importantes

- **Features Predictivas**: Disponibles desde el inicio del curso (del cuestionario)
- **Features Transaccionales**: Se complementan durante el curso
- **Predicción Temprana**: El modelo puede predecir riesgo solo con features del cuestionario
- **Coherencia**: Los perfiles fueron generados coherentemente con el rendimiento real

## 🔗 Recursos

- Dataset: `historical_dataset_with_profiles.csv`
- Código fuente: `ml-service/services/feature_engineering.py`
- Modelo: `ml-service/services/model_service.py`

