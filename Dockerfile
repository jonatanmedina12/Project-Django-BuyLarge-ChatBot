FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc postgresql-client libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . /app/

EXPOSE 8000

# No se ejecutará directamente, ahora usaremos un script de inicio
CMD ["./entrypoint.sh"]