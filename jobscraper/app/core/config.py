# config.py
# Configuracion especifica de la aplicacion
# Variables de entorno, configuracion de la aplicacion FastAPI

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    """
    Configuracion de la aplicacion usando Pydantic Settings.
    Las variables se cargan automaticamente desde el archivo .env
    """
    
    # Configuracion de la aplicacion
    PROJECT_NAME: str = "JobScraper"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Base de datos
    DATABASE_URL: str = "postgresql://usuario:password@localhost:5432/jobscraper"
    
    # Seguridad
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Configuracion de scraping
    SCRAPING_DELAY: float = 1.0
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    USER_AGENT: str = "JobScraper-Bot/1.0"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Configuracion de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx"]
    
    # Configuracion de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Configuracion de email (para notificaciones)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Configuracion de cache
    REDIS_URL: Optional[str] = None
    CACHE_EXPIRE_SECONDS: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuracion
settings = Settings()