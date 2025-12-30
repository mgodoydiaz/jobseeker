# config.py
# Configuracion global del proyecto
# Variables de entorno globales, configuracion de base de datos, APIs externas, etc.
# Este archivo centraliza toda la configuracion del proyecto

from jobscraper.app.core.config import settings

# Re-exportar settings para fácil acceso desde la raíz
__all__ = ["settings"]