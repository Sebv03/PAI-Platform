"""
Script para entrenar el modelo inicialmente
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from services.data_service import DataService
from services.feature_engineering import FeatureEngineering
from services.model_service import ModelService


def main():
    """Función principal para entrenar el modelo"""
    print("=" * 60)
    print("ENTRENAMIENTO DEL MODELO DE ML")
    print("=" * 60)
    print()
    
    # Inicializar servicios
    data_service = DataService()
    feature_engineering = FeatureEngineering()
    model_service = ModelService()
    
    try:
        # 1. Obtener datos históricos
        print("1. Obteniendo datos históricos de la base de datos...")
        historical_data = data_service.get_historical_data()
        
        if historical_data.empty:
            print("ERROR: No hay datos históricos disponibles.")
            print("Por favor, ejecuta primero el script populate_historical_data.py")
            return
        
        print(f"   [OK] Datos obtenidos: {len(historical_data)} registros")
        print()
        
        # 2. Calcular features
        print("2. Calculando features...")
        features_df = feature_engineering.calculate_features(historical_data)
        
        if features_df.empty:
            print("ERROR: No se pudieron calcular features.")
            print("Verifica que haya entregas con calificaciones en la base de datos.")
            return
        
        print(f"   [OK] Features calculadas: {len(features_df)} estudiantes-cursos")
        print(f"   [OK] Features: {', '.join(feature_engineering.get_feature_names())}")
        print()
        
        # Mostrar estadísticas de las features
        print("3. Estadísticas de las features:")
        print(features_df.describe())
        print()
        
        # 4. Entrenar modelo
        print("4. Entrenando modelo...")
        metrics = model_service.train_model(features_df)
        print()
        
        # 5. Guardar modelo
        print("5. Guardando modelo...")
        model_service.save_model()
        print()
        
        # 6. Resumen
        print("=" * 60)
        print("ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print()
        print("Métricas del modelo:")
        print(f"  - Accuracy: {metrics['accuracy']:.3f}")
        print(f"  - Precision: {metrics['precision']:.3f}")
        print(f"  - Recall: {metrics['recall']:.3f}")
        print(f"  - F1-Score: {metrics['f1_score']:.3f}")
        print()
        print(f"Modelo guardado en: {model_service.model_path}")
        print()
        print("Puedes iniciar el servidor ML con:")
        print("  python main.py")
        print("  o")
        print("  uvicorn main:app --host 0.0.0.0 --port 8001")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

