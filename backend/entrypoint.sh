#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Ejecutar las migraciones de la base de datos de Django
# Es importante asegurarse de que la base de datos esté disponible antes de ejecutar esto
# En una configuración de producción con una base de datos externa, se añadiría aquí
# una lógica de espera.

echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate

# Ejecutar el comando principal del contenedor (lo que se pasa después de este script)
# Por ejemplo: gunicorn, etc.
echo "Migraciones completadas. Iniciando el servidor..."
exec "$@"
