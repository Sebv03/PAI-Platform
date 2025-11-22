# Dockerfile para ML Service
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para modelos si no existe
RUN mkdir -p models

# Exponer puerto
EXPOSE 8001

# Comando para ejecutar el servicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]



