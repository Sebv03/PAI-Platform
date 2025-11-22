# 🚀 Guía Rápida de Despliegue

## Despliegue Rápido con Docker Compose

### 1. Preparar el servidor

```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar y configurar

```bash
git clone https://github.com/Sebv03/PAI-Platform.git
cd PAI-Platform
cp .env.example .env
nano .env  # Editar con tus valores
```

### 3. Desplegar

```bash
# Opción A: Usar el script automatizado
chmod +x deploy.sh
./deploy.sh

# Opción B: Manual
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Inicializar

```bash
# Crear administrador
docker-compose -f docker-compose.prod.yml exec backend python create_admin.py

# (Opcional) Poblar datos de prueba
docker-compose -f docker-compose.prod.yml exec backend python populate_historical_data.py
```

### 5. Verificar

- Frontend: http://tu-servidor:5173
- Backend API: http://tu-servidor:8000
- API Docs: http://tu-servidor:8000/docs
- ML Service: http://tu-servidor:8001

## Variables de Entorno Importantes

Edita el archivo `.env` con estos valores:

```env
POSTGRES_PASSWORD=tu_password_seguro
BACKEND_SECRET_KEY=genera_con_python3_-c_"import_secrets;_print(secrets.token_hex(32))"
BACKEND_CORS_ORIGINS=http://tu-dominio.com,https://tu-dominio.com
FRONTEND_API_BASE_URL=http://tu-servidor:8000
```

## Comandos Útiles

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Actualizar aplicación
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Documentación Completa

Para más detalles, consulta [GUIA_DESPLIEGUE.md](./GUIA_DESPLIEGUE.md)



