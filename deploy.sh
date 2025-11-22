#!/bin/bash

# Script de despliegue automatizado para PAI Platform
# Uso: ./deploy.sh

set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue de PAI Platform..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado. Por favor instálalo primero.${NC}"
    exit 1
fi

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado. Por favor instálalo primero.${NC}"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado.${NC}"
    echo "Creando .env desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Por favor edita el archivo .env con tus valores antes de continuar.${NC}"
        exit 1
    else
        echo -e "${RED}❌ Archivo .env.example no encontrado.${NC}"
        exit 1
    fi
fi

# Detener contenedores existentes
echo -e "${YELLOW}🛑 Deteniendo contenedores existentes...${NC}"
docker-compose -f docker-compose.prod.yml down || true

# Construir imágenes
echo -e "${YELLOW}🔨 Construyendo imágenes Docker...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Levantar servicios
echo -e "${YELLOW}🚀 Levantando servicios...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que la base de datos esté lista
echo -e "${YELLOW}⏳ Esperando a que la base de datos esté lista...${NC}"
sleep 10

# Verificar que los servicios están corriendo
echo -e "${YELLOW}🔍 Verificando servicios...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Crear usuario administrador (si no existe)
echo -e "${YELLOW}👤 Creando usuario administrador...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python create_admin.py || echo "Usuario administrador ya existe o hubo un error"

echo -e "${GREEN}✅ Despliegue completado exitosamente!${NC}"
echo ""
echo "Servicios disponibles en:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000"
echo "  - ML Service: http://localhost:8001"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Para ver los logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "Para detener los servicios:"
echo "  docker-compose -f docker-compose.prod.yml down"



