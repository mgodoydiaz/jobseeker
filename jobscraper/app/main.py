# main.py
# Punto de entrada principal de la aplicación FastAPI
# Aquí se configurará la aplicación, middlewares, rutas y se iniciará el servidor
# IMPLEMENTADO: Aplicación FastAPI completa con middlewares, CORS, manejo de errores

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import time
import logging
from typing import Union

from .core.config import settings
from .database.connection import create_tables
from .api import routes


# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Se ejecuta al inicio y al cierre de la aplicación.
    """
    # Startup
    logger.info("🚀 Iniciando JobScraper API...")
    
    # Crear tablas de base de datos si no existen
    try:
        create_tables()
        logger.info("✅ Tablas de base de datos verificadas/creadas")
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")
        raise
    
    logger.info(f"🌐 API disponible en: http://localhost:8000")
    logger.info(f"📚 Documentación en: http://localhost:8000/docs")
    logger.info(f"🔧 Configuración: {settings.PROJECT_NAME} v{settings.VERSION}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando JobScraper API...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    **JobScraper API** - Backend para scraping y gestión de ofertas laborales
    
    ## Características
    
    * **Gestión de usuarios** con autenticación JWT
    * **Scraping automatizado** de múltiples sitios web
    * **Búsqueda avanzada** de ofertas laborales con filtros
    * **Tracking de interacciones** y historial de búsquedas
    * **Estadísticas y analytics** detallados
    * **API REST completa** con documentación automática
    
    ## Autenticación
    
    La API utiliza **JWT (JSON Web Tokens)** para autenticación.
    Incluye el token en el header: `Authorization: Bearer <token>`
    
    ## Rate Limiting
    
    * **60 requests/minuto** por IP
    * **1000 requests/hora** por IP
    
    ## Soporte
    
    Para soporte técnico, contacta al equipo de desarrollo.
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ==================== MIDDLEWARES ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware (seguridad)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )


# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de todas las requests.
    """
    start_time = time.time()
    
    # Log de request entrante
    logger.info(f"📥 {request.method} {request.url.path} - IP: {request.client.host}")
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    # Log de response
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Agregar header con tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# ==================== MANEJADORES DE ERRORES ====================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Manejador personalizado para errores HTTP.
    """
    logger.error(f"❌ HTTP Error {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador personalizado para errores de validación de Pydantic.
    """
    logger.error(f"❌ Validation Error: {exc.errors()} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Error de validación en los datos enviados",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador general para errores no capturados.
    """
    logger.error(f"💥 Unexpected Error: {str(exc)} - Path: {request.url.path}", exc_info=True)
    
    # En producción, no mostrar detalles del error
    if settings.DEBUG:
        error_detail = str(exc)
    else:
        error_detail = "Error interno del servidor"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": error_detail,
            "status_code": 500,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# ==================== RUTAS PRINCIPALES ====================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    Retorna información básica de la aplicación.
    """
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR,
        "timestamp": time.time()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de health check para monitoreo.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": time.time(),
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/info", tags=["Info"])
async def app_info():
    """
    Información detallada de la aplicación.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Backend para scraping y gestión de ofertas laborales",
        "api_version": "v1",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json",
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "rate_limits": {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "per_hour": settings.RATE_LIMIT_PER_HOUR
        },
        "features": [
            "Gestión de usuarios con JWT",
            "Scraping automatizado",
            "Búsqueda avanzada de ofertas",
            "Tracking de interacciones",
            "Estadísticas y analytics",
            "API REST completa"
        ],
        "timestamp": time.time()
    }


# ==================== INCLUIR ROUTERS ====================

# Incluir todas las rutas de la API v1
app.include_router(
    routes.router,
    prefix=settings.API_V1_STR,
    tags=["API v1"]
)


# ==================== CONFIGURACIÓN ADICIONAL ====================

# Configurar headers de seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Agregar headers de seguridad a todas las responses.
    """
    response = await call_next(request)
    
    # Headers de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Header personalizado
    response.headers["X-API-Version"] = settings.VERSION
    response.headers["X-Powered-By"] = settings.PROJECT_NAME
    
    return response


# ==================== EVENTOS DE APLICACIÓN ====================

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Configuraciones adicionales de startup.
    """
    logger.info("🔧 Configurando servicios adicionales...")
    
    # Aquí se pueden agregar configuraciones adicionales como:
    # - Conexión a Redis
    # - Inicialización de servicios externos
    # - Configuración de tareas en background
    
    logger.info("✅ Servicios adicionales configurados")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación.
    Limpieza de recursos.
    """
    logger.info("🧹 Limpiando recursos...")
    
    # Aquí se pueden agregar tareas de limpieza como:
    # - Cerrar conexiones a servicios externos
    # - Guardar estado de la aplicación
    # - Cancelar tareas en background
    
    logger.info("✅ Recursos limpiados correctamente")


# ==================== CONFIGURACIÓN PARA DESARROLLO ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando servidor de desarrollo...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )