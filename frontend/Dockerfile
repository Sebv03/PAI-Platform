# Dockerfile para Frontend (React + Vite)
# Etapa 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Variables de entorno para el build (se pasan como ARG en docker-compose)
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_ML_SERVICE_URL=http://localhost:8001

# Vite necesita que las variables de entorno estén disponibles en tiempo de build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_ML_SERVICE_URL=$VITE_ML_SERVICE_URL

# Build de la aplicación
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:alpine

# Copiar archivos build desde la etapa anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]

