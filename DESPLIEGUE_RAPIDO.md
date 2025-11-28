# 🚀 Despliegue Rápido - Plataforma PAI

Guía rápida para subir tu proyecto a internet de forma GRATUITA en menos de 30 minutos.

## ⚡ Opción Rápida: Render.com (Recomendada)

### Paso 1: Preparar Repositorio
- ✅ Asegúrate de que tu código está en GitHub
- ✅ Verifica que los archivos `requirements.txt` y `package.json` existen

### Paso 2: Crear Base de Datos
1. Ir a [render.com](https://render.com) y crear cuenta (con GitHub)
2. Click "New +" → "PostgreSQL"
3. Configurar:
   - Name: `pai-database`
   - Plan: Free
   - Region: Oregon (o más cercano)
4. ⚠️ **Guardar** la "Internal Database URL"

### Paso 3: Desplegar Backend
1. Click "New +" → "Web Service"
2. Conectar repositorio: PAI-Platform
3. Configurar:
   ```
   Name: pai-backend
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Variables de Entorno:
   ```
   DATABASE_URL = [Internal Database URL de paso 2]
   SECRET_KEY = [generar con: python -c "import secrets; print(secrets.token_hex(32))"]
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   BACKEND_CORS_ORIGINS = https://pai-frontend.onrender.com
   ```
5. Plan: Free
6. Click "Create Web Service"
7. URL resultante: `https://pai-backend.onrender.com`

### Paso 4: Desplegar ML Service
1. Click "New +" → "Web Service"
2. Mismo repositorio: PAI-Platform
3. Configurar:
   ```
   Name: pai-ml-service
   Root Directory: ml-service
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. Variables de Entorno:
   ```
   DATABASE_URL = [misma URL del paso 2]
   CORS_ORIGINS = https://pai-frontend.onrender.com
   MODEL_PATH = models/risk_prediction_model.pkl
   RISK_THRESHOLD = 0.5
   ```
5. URL resultante: `https://pai-ml-service.onrender.com`

### Paso 5: Desplegar Frontend
1. Crear archivo `frontend/.env.production`:
   ```env
   VITE_API_BASE_URL=https://pai-backend.onrender.com
   VITE_ML_SERVICE_URL=https://pai-ml-service.onrender.com
   ```
2. En Render: Click "New +" → "Static Site"
3. Configurar:
   ```
   Name: pai-frontend
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```
4. Environment Variables:
   ```
   VITE_API_BASE_URL = https://pai-backend.onrender.com
   VITE_ML_SERVICE_URL = https://pai-ml-service.onrender.com
   ```
5. URL resultante: `https://pai-frontend.onrender.com`

### Paso 6: Inicializar Base de Datos
Desde tu computadora local:
```bash
cd backend
export DATABASE_URL="[External Database URL de Render - diferente a Internal]"
python setup_complete_platform.py
```

O desde Render Shell:
1. Dashboard del backend → "Shell"
2. Ejecutar: `python setup_complete_platform.py`

### Paso 7: ¡Listo! 🎉
Tu plataforma está en:
- Frontend: `https://pai-frontend.onrender.com`
- Backend API: `https://pai-backend.onrender.com/docs`
- ML Service: `https://pai-ml-service.onrender.com/docs`

---

## 📝 Notas Importantes

### ⚠️ Servicios se Duermen
- Los servicios gratuitos de Render se "duermen" después de 15 minutos sin uso
- La primera carga después de dormir toma ~30 segundos
- **Solución**: Usar un servicio de ping (ej: [UptimeRobot](https://uptimerobot.com) - gratis)

### ⚠️ PostgreSQL Gratuito
- Se elimina después de 90 días sin uso
- Si planeas usarlo activamente, no hay problema

### ⚠️ URLs Internas vs Externas
- **Internal Database URL**: Para conectar desde servicios dentro de Render
- **External Database URL**: Para conectar desde fuera de Render (tu computadora)

---

## 🔄 Opción Alternativa: Usar render.yaml

Si prefieres desplegar todo de una vez:

1. El proyecto incluye `render.yaml` en la raíz
2. En Render: "New +" → "Blueprint"
3. Conectar repositorio
4. Render creará todos los servicios automáticamente

Luego solo necesitas:
- Generar SECRET_KEY manualmente y agregarlo
- Actualizar BACKEND_CORS_ORIGINS con la URL del frontend
- Inicializar la base de datos

---

## 📚 Documentación Completa

Para más detalles, opciones alternativas y solución de problemas, consulta:
- **[HOSTING_GRATUITO_COMPLETO.txt](./HOSTING_GRATUITO_COMPLETO.txt)** - Guía completa con todas las opciones

---

## 🆘 Problemas Comunes

### Error: "Service failed to start"
- Verifica que el Start Command use `$PORT` (no un número fijo)
- Revisa los logs en el dashboard

### Error: CORS
- Verifica que `BACKEND_CORS_ORIGINS` incluya la URL exacta del frontend
- No incluyas "/" al final

### Frontend no conecta con backend
- Verifica que las variables `VITE_API_BASE_URL` y `VITE_ML_SERVICE_URL` estén correctas
- Reconstruye el frontend después de cambiar variables

---

¡Buena suerte con tu despliegue! 🚀


