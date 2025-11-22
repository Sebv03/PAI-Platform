# 🚀 Guía de Despliegue a Producción - PAI Platform

Esta guía te ayudará a desplegar la plataforma PAI en un entorno de producción (servidor virtual, VPS, cloud, etc.).

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Opciones de Hosting](#opciones-de-hosting)
3. [Configuración con Docker](#configuración-con-docker)
4. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Configuración de Dominio y SSL](#configuración-de-dominio-y-ssl)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 📦 Requisitos Previos

- **Servidor/VPS** con:
  - Ubuntu 20.04+ o similar (Linux)
  - Mínimo 2GB RAM (recomendado 4GB+)
  - 20GB+ espacio en disco
  - Acceso SSH
- **Docker** y **Docker Compose** instalados
- **Dominio** (opcional pero recomendado)
- **Conocimientos básicos** de Linux y Docker

---

## 🌐 Opciones de Hosting

### Opción 1: DigitalOcean (Recomendado para empezar)
- **Ventajas**: Simple, económico, buena documentación
- **Precio**: ~$12-24/mes (Droplet de 2-4GB RAM)
- **Link**: https://www.digitalocean.com/

### Opción 2: AWS EC2
- **Ventajas**: Escalable, muchos servicios adicionales
- **Precio**: ~$10-20/mes (t2.small o t3.small)
- **Link**: https://aws.amazon.com/ec2/

### Opción 3: Google Cloud Platform (GCP)
- **Ventajas**: Integración con servicios de Google
- **Precio**: Similar a AWS
- **Link**: https://cloud.google.com/

### Opción 4: Azure
- **Ventajas**: Integración con servicios Microsoft
- **Precio**: Similar a AWS
- **Link**: https://azure.microsoft.com/

### Opción 5: Vultr / Linode
- **Ventajas**: Económicos, buen rendimiento
- **Precio**: ~$6-12/mes
- **Link**: https://www.vultr.com/ o https://www.linode.com/

---

## 🐳 Configuración con Docker

### Estructura de Servicios

La aplicación consta de 4 servicios principales:

1. **PostgreSQL** - Base de datos
2. **Backend** (FastAPI) - API principal en puerto 8000
3. **ML Service** (FastAPI) - Microservicio ML en puerto 8001
4. **Frontend** (React + Vite) - Interfaz web en puerto 5173

---

## 📝 Despliegue Paso a Paso

### Paso 1: Preparar el Servidor

```bash
# Conectarse al servidor via SSH
ssh usuario@tu-servidor-ip

# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### Paso 2: Clonar el Repositorio

```bash
# Instalar Git si no está instalado
sudo apt install git -y

# Clonar el repositorio
cd ~
git clone https://github.com/Sebv03/PAI-Platform.git
cd PAI-Platform
```

### Paso 3: Configurar Variables de Entorno

```bash
# Crear archivo .env en la raíz del proyecto
nano .env
```

Contenido del archivo `.env`:

```env
# Base de Datos
POSTGRES_USER=admin
POSTGRES_PASSWORD=TU_PASSWORD_SEGURO_AQUI
POSTGRES_DB=pai_db
POSTGRES_PORT=5432

# Backend
BACKEND_SECRET_KEY=GENERA_UNA_CLAVE_SECRETA_AQUI
BACKEND_ALGORITHM=HS256
BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=http://tu-dominio.com,https://tu-dominio.com

# URLs (ajustar según tu dominio)
BACKEND_URL=http://tu-servidor-ip:8000
ML_SERVICE_URL=http://tu-servidor-ip:8001
FRONTEND_URL=http://tu-dominio.com

# ML Service
ML_RISK_THRESHOLD=0.5
```

**⚠️ IMPORTANTE**: Genera una clave secreta segura:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Paso 4: Construir y Levantar los Servicios

```bash
# Construir las imágenes
docker-compose build

# Levantar los servicios
docker-compose up -d

# Ver los logs
docker-compose logs -f
```

### Paso 5: Inicializar la Base de Datos

```bash
# Ejecutar migraciones (si las tienes)
docker-compose exec backend python -m alembic upgrade head

# Crear usuario administrador
docker-compose exec backend python create_admin.py

# (Opcional) Poblar datos de prueba
docker-compose exec backend python populate_historical_data.py
```

### Paso 6: Verificar que Todo Funciona

```bash
# Verificar que los contenedores están corriendo
docker-compose ps

# Probar los endpoints
curl http://localhost:8000/
curl http://localhost:8001/
```

---

## 🔧 Configuración de Variables de Entorno

### Backend (.env o variables de entorno)

Las variables se pueden configurar de dos formas:

1. **Archivo .env** (recomendado para desarrollo)
2. **Variables de entorno del sistema** (recomendado para producción)

Para producción, edita `docker-compose.yml` y agrega las variables en la sección `environment`:

```yaml
backend:
  environment:
    - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    - SECRET_KEY=${BACKEND_SECRET_KEY}
    - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
```

---

## 🌍 Configuración de Dominio y SSL

### Opción 1: Nginx como Reverse Proxy (Recomendado)

```bash
# Instalar Nginx
sudo apt install nginx -y

# Crear configuración
sudo nano /etc/nginx/sites-available/pai-platform
```

Contenido de la configuración:

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# Configuración HTTPS
server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # Certificados SSL (generados con Certbot)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ML Service
    location /ml/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar el sitio
sudo ln -s /etc/nginx/sites-available/pai-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Opción 2: Certbot para SSL Gratuito

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática (ya está configurado)
sudo certbot renew --dry-run
```

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
docker-compose logs -f ml-service
docker-compose logs -f frontend
```

### Reiniciar Servicios

```bash
# Reiniciar todos
docker-compose restart

# Reiniciar servicio específico
docker-compose restart backend
```

### Actualizar la Aplicación

```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir y levantar
docker-compose build
docker-compose up -d
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U admin pai_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose exec -T db psql -U admin pai_db < backup_20241117_120000.sql
```

### Monitoreo de Recursos

```bash
# Ver uso de recursos
docker stats

# Ver espacio en disco
df -h
docker system df
```

---

## 🔒 Seguridad en Producción

### Checklist de Seguridad

- [ ] Cambiar todas las contraseñas por defecto
- [ ] Usar contraseñas seguras (mínimo 16 caracteres)
- [ ] Configurar firewall (UFW)
- [ ] Habilitar SSL/HTTPS
- [ ] Configurar backups automáticos
- [ ] Limitar acceso SSH (solo desde IPs conocidas)
- [ ] Actualizar el sistema regularmente
- [ ] Configurar rate limiting en Nginx
- [ ] Revisar logs regularmente

### Configurar Firewall (UFW)

```bash
# Instalar UFW
sudo apt install ufw -y

# Permitir SSH (¡IMPORTANTE! Hacerlo primero)
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## 🐛 Solución de Problemas Comunes

### Los servicios no inician

```bash
# Ver logs detallados
docker-compose logs

# Verificar puertos ocupados
sudo netstat -tulpn | grep LISTEN

# Reiniciar Docker
sudo systemctl restart docker
```

### Error de conexión a la base de datos

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps db

# Ver logs de la base de datos
docker-compose logs db

# Verificar variables de entorno
docker-compose exec backend env | grep DATABASE
```

### Frontend no se conecta al backend

- Verificar que `BACKEND_CORS_ORIGINS` incluye la URL del frontend
- Verificar que las URLs en `frontend/src/services/api.js` son correctas
- Revisar la consola del navegador para errores CORS

---

## 📚 Recursos Adicionales

- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt / Certbot](https://certbot.eff.org/)

---

## ✅ Checklist Final de Despliegue

- [ ] Servidor configurado con Docker
- [ ] Repositorio clonado
- [ ] Variables de entorno configuradas
- [ ] Servicios levantados y funcionando
- [ ] Base de datos inicializada
- [ ] Usuario administrador creado
- [ ] Dominio configurado (opcional)
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Firewall configurado
- [ ] Backups configurados
- [ ] Monitoreo configurado

---

**¡Felicitaciones! 🎉 Tu plataforma PAI está lista para producción.**

Para soporte adicional, revisa los logs o consulta la documentación de cada servicio.



