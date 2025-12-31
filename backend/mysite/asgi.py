"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from fastapi.staticfiles import StaticFiles
from jobscraper.app.main import app as fastapi_app
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# Importa la aplicación ASGI de Django
django_asgi_app = get_asgi_application()

# Crea una nueva aplicación FastAPI que servirá como punto de montaje principal
from fastapi import FastAPI
application = FastAPI()

# Monta la documentación de la API y las rutas de la API principal bajo /api/v1
application.mount("/api/v1", fastapi_app)

# Monta la aplicación Django para manejar todas las demás rutas
# Es importante montar esto *después* de las rutas de FastAPI
application.mount("/", django_asgi_app)
