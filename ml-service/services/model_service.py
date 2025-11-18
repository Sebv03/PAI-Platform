"""
Servicio del modelo de Machine Learning
"""

import pickle
import os
import sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings
from services.feature_engineering import FeatureEngineering


class ModelService:
    """Servicio para manejar el modelo de ML"""
    
    def __init__(self):
        self.model = None
        self.feature_engineering = FeatureEngineering()
        self.model_path = Path(settings.MODEL_PATH)
        self.model_dir = Path(settings.MODEL_DIR)
        
        # Crear directorio de modelos si no existe
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Intentar cargar modelo existente
        self.load_model()
    
    def is_model_loaded(self) -> bool:
        """Verifica si el modelo está cargado"""
        return self.model is not None
    
    def train_model(self, features_df):
        """
        Entrena el modelo con los datos de features
        
        Args:
            features_df: DataFrame con las features calculadas
        
        Returns:
            dict con métricas del modelo
        """
        if features_df.empty:
            raise ValueError("El DataFrame de features está vacío")
        
        # Obtener nombres de features
        feature_names = self.feature_engineering.get_feature_names()
        
        # Verificar que todas las features estén presentes
        missing_features = [f for f in feature_names if f not in features_df.columns]
        if missing_features:
            raise ValueError(f"Faltan features: {missing_features}")
        
        # Preparar X (features) y y (target)
        X = features_df[feature_names].values
        y = self.feature_engineering.calculate_target_variable(features_df).values
        
        # Verificar que haya datos de ambas clases
        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            print(f"Advertencia: Solo hay una clase en los datos: {unique_classes}")
            # Si solo hay una clase, crear datos sintéticos para la otra
            if 0 not in unique_classes:
                # Agregar algunos ejemplos de clase 0 (riesgo bajo)
                n_samples = min(10, len(X))
                X_balanced = np.vstack([X, X[:n_samples] * 0.5])  # Reducir features para riesgo bajo
                y_balanced = np.hstack([y, np.zeros(n_samples)])
                X, y = X_balanced, y_balanced
            elif 1 not in unique_classes:
                # Agregar algunos ejemplos de clase 1 (riesgo alto)
                n_samples = min(10, len(X))
                X_balanced = np.vstack([X, X[:n_samples] * 1.5])  # Aumentar features para riesgo alto
                y_balanced = np.hstack([y, np.ones(n_samples)])
                X, y = X_balanced, y_balanced
        
        # Dividir en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Crear y entrenar el modelo
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'  # Balancear clases si hay desbalance
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluar el modelo
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        print("\n=== Métricas del Modelo ===")
        print(f"Accuracy: {metrics['accuracy']:.3f}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall: {metrics['recall']:.3f}")
        print(f"F1-Score: {metrics['f1_score']:.3f}")
        print("\n=== Reporte de Clasificación ===")
        print(classification_report(y_test, y_pred, target_names=['Riesgo Bajo', 'Riesgo Alto']))
        
        return metrics
    
    def predict(self, X):
        """
        Hace una predicción con el modelo
        
        Args:
            X: Array o lista de features
        
        Returns:
            Array de predicciones (0 = riesgo bajo, 1 = riesgo alto)
        """
        if self.model is None:
            raise ValueError("El modelo no está entrenado. Llama a train_model() primero.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Retorna las probabilidades de cada clase
        
        Args:
            X: Array o lista de features
        
        Returns:
            Array de probabilidades [prob_riesgo_bajo, prob_riesgo_alto]
        """
        if self.model is None:
            raise ValueError("El modelo no está entrenado. Llama a train_model() primero.")
        
        return self.model.predict_proba(X)
    
    def save_model(self):
        """Guarda el modelo en disco"""
        if self.model is None:
            raise ValueError("No hay modelo para guardar")
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Modelo guardado en: {self.model_path}")
    
    def load_model(self) -> bool:
        """
        Carga el modelo desde disco
        
        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        if not self.model_path.exists():
            print(f"Modelo no encontrado en: {self.model_path}")
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Modelo cargado desde: {self.model_path}")
            return True
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            return False

