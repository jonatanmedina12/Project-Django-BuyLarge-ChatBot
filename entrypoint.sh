#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté disponible..."
until PGPASSWORD=$DB_PASSWORD psql -h db -U $DB_USER -d $DB_NAME -c '\q'; do
  >&2 echo "Base de datos no disponible aún - esperando..."
  sleep 2
done
echo "Base de datos disponible!"

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Cargar datos de demostración
echo "Cargando datos de demostración..."
python manage.py load_demo_data

# Iniciar el servidor
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000