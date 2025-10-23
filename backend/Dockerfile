# backend/Dockerfile
# Usa una imagen base de Python oficial
FROM python:3.11-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt y luego instala las dependencias
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia el resto del código de la aplicación
COPY ./app /app/app

# Expone el puerto que usa FastAPI
EXPOSE 8000

# Define el comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]