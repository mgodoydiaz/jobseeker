# Usar una imagen oficial de Python como imagen base
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar las dependencias de Python
COPY ./mysite/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el punto de entrada y darle permisos de ejecución
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copiar el resto del código de la aplicación
COPY . /app/

# Exponer el puerto 8000 para que la aplicación sea accesible
EXPOSE 8000

# Ejecutar el script de punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para iniciar el servidor de Django
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
