# Dockerfile para Chandra OCR API
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY pyproject.toml ./
COPY uv.lock* ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto (fly.io usará la variable PORT)
EXPOSE 8080

# Comando para ejecutar la API
CMD python -m chandra.scripts.run_api

