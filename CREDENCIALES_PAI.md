# 🔐 Credenciales de Acceso - Plataforma PAES PAI

## 👨‍🏫 Profesor de Matemáticas

**Email:** `profesor.matematicas@pai.cl`  
**Password:** `profesor123`  
**Nombre:** Profesor Matemáticas

Este profesor tiene acceso a los siguientes cursos PAES:
- [M1] Números
- [M1] Álgebra y Funciones
- [M1] Geometría
- [M1] Probabilidad y Estadística

---

## 👨‍🎓 Estudiante de Ejemplo

**Email:** `juan.perez.0@estudiante.pai.cl`  
**Password:** `estudiante123`  
**Nombre:** Juan Pérez  
**Nivel:** 1° medio  
**Edad:** 15 años

**NOTA:** Todos los 200 estudiantes tienen la misma contraseña: `estudiante123`

---

## 👨‍💼 Administrador

Si necesitas acceder como administrador, puedes usar el usuario administrador creado anteriormente, o crear uno nuevo con:

```python
python backend/create_admin.py
```

---

## 📊 Datos Generados

- **200 estudiantes** con perfiles completos (14-18 años, 1° a 4° medio)
- **912 inscripciones** en cursos PAES
- **97 tareas** distribuidas en 15 cursos
- **3,278 entregas** con calificaciones (escala 1.0-7.0)

Estos datos están listos para:
- ✅ Entrenar el modelo ML (`POST /ml/train`)
- ✅ Probar predicciones de riesgo académico
- ✅ Visualizar datos históricos en el Admin Dashboard

---

## 🚀 Próximos Pasos

1. **Entrenar el modelo ML:**
   - Inicia sesión como administrador
   - Ve al Admin Dashboard
   - Haz clic en "Entrenar Modelo ML"

2. **Probar predicciones:**
   - Como profesor: Ve a "Ver Predicciones de Riesgo" en cualquier curso
   - Como administrador: Usa el panel de búsqueda de estudiantes

3. **Iniciar sesión:**
   - Frontend: http://localhost:5173
   - Usa las credenciales de arriba





