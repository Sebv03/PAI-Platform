"""
Código completo del notebook de Google Colab
Copia y pega cada sección como una celda nueva en Colab
"""

# ============================================================================
# CELDA 1: Instalación de librerías
# ============================================================================
"""
!pip install pandas numpy scikit-learn matplotlib seaborn -q
"""

# ============================================================================
# CELDA 2: Importación de librerías
# ============================================================================
"""
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

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Librerías importadas correctamente")
"""

# ============================================================================
# CELDA 3: Función de generación de datos
# ============================================================================
"""
# NOTA: Esta función es larga, asegúrate de copiarla completa desde
# ml_service_colab_utils.py o desde GUIA_NOTEBOOK_COLAB.md
# Aquí está la versión simplificada:

def generate_synthetic_data(n_students=200, n_courses=10, tasks_per_course=8, random_seed=42):
    # Ver ml_service_colab_utils.py para la implementación completa
    pass
"""

# ============================================================================
# CELDA 4: Generar dataset
# ============================================================================
"""
# Generar datos
print("🔄 Generando dataset sintético...")
df = generate_synthetic_data(n_students=200, n_courses=10, tasks_per_course=8)

print(f"✅ Dataset generado: {len(df)} registros")
print(f"   - Estudiantes únicos: {df['student_id'].nunique()}")
print(f"   - Cursos únicos: {df['course_id'].nunique()}")
print(f"   - Entregas: {df['submission_id'].notna().sum()}")
print(f"   - Sin entregar: {df['submission_id'].isna().sum()}")

df.head(10)
"""

# ============================================================================
# CELDA 5: Feature Engineering
# ============================================================================
"""
def calculate_features(data: pd.DataFrame) -> pd.DataFrame:
    # Convertir fechas
    date_columns = ['due_date', 'submitted_at', 'task_created_at', 'enrollment_date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])
    
    grouped = data.groupby(['student_id', 'course_id'])
    results = []
    
    for (student_id, course_id), group in grouped:
        # 1. Tasa de retraso
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
        
        # 3. Promedio de notas (normalizado)
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
"""

# ============================================================================
# CELDA 6: Calcular features y target
# ============================================================================
"""
# Calcular features
print("🔄 Calculando features...")
features_df = calculate_features(df)
print(f"✅ Features calculadas: {len(features_df)} estudiantes-cursos")

# Calcular target
average_grade_original = features_df['average_grade'] * 6.0 + 1.0
features_df['risk'] = ((average_grade_original < 4.0) | (features_df['non_submission_rate'] > 0.5)).astype(int)

print(f"📊 Distribución de riesgo:")
print(features_df['risk'].value_counts())
features_df.head(10)
"""

# ============================================================================
# CELDA 7: Preparar datos y entrenar modelo
# ============================================================================
"""
# Preparar datos
feature_names = ['submission_delay_rate', 'non_submission_rate', 'average_grade', 'grade_variability']
X = features_df[feature_names].values
y = features_df['risk'].values

# Dividir datos
indices = np.arange(len(features_df))
train_indices, test_indices = train_test_split(indices, test_size=0.2, random_state=42, stratify=y)
X_train, X_test = X[train_indices], X[test_indices]
y_train, y_test = y[train_indices], y[test_indices]

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
print("🔄 Entrenando modelo...")
model.fit(X_train, y_train)
print("✅ Modelo entrenado")

# Importancia de features
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\n📊 Importancia de Features:")
print(feature_importance)
"""

# ============================================================================
# CELDA 8: Evaluar modelo
# ============================================================================
"""
# Predicciones
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Métricas
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print("=" * 60)
print("📊 MÉTRICAS DEL MODELO")
print("=" * 60)
print(f"✅ Accuracy:  {accuracy:.4f}")
print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall:    {recall:.4f}")
print(f"✅ F1-Score:  {f1:.4f}")
print("\n" + classification_report(y_test, y_pred, target_names=['Riesgo Bajo', 'Riesgo Alto']))
"""

# ============================================================================
# CELDA 9: Visualizaciones
# ============================================================================
"""
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

# Importancia de features
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance, x='importance', y='feature', palette='viridis')
plt.title('Importancia de Features', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
"""

# ============================================================================
# CELDA 10: Tabla de predicciones
# ============================================================================
"""
# Tabla de predicciones
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
print("📋 Tabla de Predicciones (muestra):")
print(predictions_df.head(20))
print(f"\n📊 Aciertos: {predictions_df['correct'].sum()}/{len(predictions_df)} ({predictions_df['correct'].mean()*100:.1f}%)")
"""

