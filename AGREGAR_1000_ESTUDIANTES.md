# 📝 Guía: Agregar 1000 Estudiantes al Dataset Histórico

Este documento explica cómo agregar 1000 estudiantes adicionales al dataset histórico.

## 📋 Pasos

### Paso 1: Activar Entorno Virtual

**Windows:**
```bash
cd backend
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
source venv/bin/activate
```

### Paso 2: Verificar que bcrypt esté instalado

```bash
pip install bcrypt
```

### Paso 3: Ejecutar el Script

```bash
python add_1000_students.py
```

El script:
1. Generará 1000 estudiantes con nombres y emails únicos
2. Los inscribirá en cursos existentes (1-3 cursos por estudiante)
3. Creará entregas y calificaciones para ellos
4. Mantendrá los datos existentes intactos

### Paso 4: Exportar Dataset Actualizado

Después de agregar los estudiantes, exporta el nuevo dataset:

```bash
cd ..
python export_historical_data_to_csv.py
```

Esto creará `datasets/historical_dataset.csv` con todos los datos incluyendo los 1000 estudiantes adicionales.

## 📊 Resultados Esperados

Después de ejecutar el script verás:

```
[OK] Creados 1000 estudiantes adicionales
[OK] Creadas X inscripciones adicionales
[OK] Creadas X entregas adicionales
[OK] Asignadas X calificaciones adicionales
```

El dataset actualizado tendrá:
- ~1026 estudiantes totales (26 originales + 1000 nuevos)
- Miles de inscripciones adicionales
- Miles de entregas adicionales
- Muchos más datos para entrenar el modelo ML

## ⚠️ Notas

- El script procesa en lotes para mejor rendimiento
- Los estudiantes se generan con nombres y emails únicos
- Cada estudiante se inscribe en 1-3 cursos aleatorios
- Las entregas siguen el mismo patrón que los datos originales (70% entrega, 35% tardías)
- Las calificaciones varían entre 3.5 y 6.5 (con penalizaciones por retraso)

## 🔍 Verificar Resultados

Para verificar que los estudiantes se agregaron:

```bash
# Conectarse a PostgreSQL y ejecutar:
SELECT COUNT(*) FROM users WHERE role = 'ESTUDIANTE';
```

Deberías ver aproximadamente 1026 estudiantes.

