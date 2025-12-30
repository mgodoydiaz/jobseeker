# database_models.py
# Modelos de base de datos (SQLAlchemy ORM)
# Definicion de tablas y relaciones de la base de datos
# ACTUALIZADO: Modelos expandidos para soportar sistema completo de usuarios, scraping e historial

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database.connection import Base


# ==================== ENUMS PARA BASE DE DATOS ====================

class JobStatusEnum(enum.Enum):
    """Estados de ofertas laborales en BD"""
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    DRAFT = "draft"


class ApplicationStatusEnum(enum.Enum):
    """Estados de postulaciones en BD"""
    PENDING = "pending"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class ScrapingStatusEnum(enum.Enum):
    """Estados de scraping en BD"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class UserRoleEnum(enum.Enum):
    """Roles de usuario en BD"""
    USER = "user"
    ADMIN = "admin"
    SCRAPER = "scraper"


# ==================== MODELOS PRINCIPALES ====================

class User(Base):
    """
    Modelo expandido para usuarios del sistema.
    Incluye autenticacion, roles y perfil detallado.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # JSON para almacenar perfil flexible (habilidades, experiencia, etc.)
    perfil_json = Column(JSON, nullable=True, default={})
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    job_interactions = relationship("UserJobInteraction", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    scraping_jobs = relationship("ScrapingJob", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, nombre='{self.nombre}', email='{self.email}')>"


class Company(Base):
    """
    Modelo expandido para empresas que publican ofertas laborales.
    Incluye informacion adicional para mejor categorizacion.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    sector = Column(String(100), nullable=True, index=True)
    sitio_web = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    tamano = Column(String(50), nullable=True)  # startup, pequena, mediana, grande
    ubicacion = Column(String(255), nullable=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacion con ofertas laborales
    ofertas = relationship("JobOffer", back_populates="empresa")

    def __repr__(self):
        return f"<Company(id={self.id}, nombre='{self.nombre}')>"


class JobOffer(Base):
    """
    Modelo expandido para ofertas laborales scrapeadas.
    Incluye campos adicionales para mejor categorizacion y matching.
    """
    __tablename__ = "job_offers"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    ubicacion = Column(String(255), nullable=True, index=True)
    salario = Column(Numeric(10, 2), nullable=True)  # Decimal para manejar montos
    fecha_publicacion = Column(DateTime(timezone=True), nullable=True, index=True)
    url = Column(String(500), nullable=False, unique=True)  # URL única para evitar duplicados
    fecha_scrapeo = Column(DateTime(timezone=True), server_default=func.now())
    
    # Campos adicionales para mejor categorizacion
    status = Column(SQLEnum(JobStatusEnum), default=JobStatusEnum.ACTIVE, nullable=False, index=True)
    requisitos = Column(JSON, nullable=True, default=[])  # Lista de requisitos
    beneficios = Column(JSON, nullable=True, default=[])  # Lista de beneficios
    modalidad = Column(String(50), nullable=True, index=True)  # remoto, presencial, hibrido
    tipo_contrato = Column(String(50), nullable=True, index=True)  # indefinido, temporal, freelance
    nivel_experiencia = Column(String(50), nullable=True, index=True)  # junior, mid, senior
    
    # Foreign Key a Company
    empresa_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    empresa = relationship("Company", back_populates="ofertas")
    user_interactions = relationship("UserJobInteraction", back_populates="job")

    def __repr__(self):
        return f"<JobOffer(id={self.id}, titulo='{self.titulo}', empresa_id={self.empresa_id})>"


# ==================== MODELOS DE SCRAPING ====================

class ScrapingSource(Base):
    """
    Modelo para configuración de fuentes de scraping.
    Define como scrapear cada sitio web especifico.
    """
    __tablename__ = "scraping_sources"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    base_url = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Configuracion de scraping en JSON
    selectors = Column(JSON, nullable=True, default={})  # CSS selectors
    headers = Column(JSON, nullable=True, default={})    # HTTP headers
    delay_seconds = Column(Numeric(4, 2), default=1.0, nullable=False)
    max_pages = Column(Integer, default=10, nullable=False)
    
    # Estadisticas
    total_jobs_scraped = Column(Integer, default=0, nullable=False)
    last_scrape_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    scraping_jobs = relationship("ScrapingJob", back_populates="source")

    def __repr__(self):
        return f"<ScrapingSource(id={self.id}, nombre='{self.nombre}')>"


class ScrapingJob(Base):
    """
    Modelo para trabajos de scraping individuales.
    Registra cada ejecucion de scraping con sus parametros y resultados.
    """
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("scraping_sources.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Usuario que inicio el scraping
    
    # Parametros de busqueda
    search_terms = Column(JSON, nullable=True, default=[])      # Terminos de busqueda
    location_filters = Column(JSON, nullable=True, default=[])  # Filtros de ubicacion
    max_results = Column(Integer, default=100, nullable=False)
    
    # Estado y timing
    status = Column(SQLEnum(ScrapingStatusEnum), default=ScrapingStatusEnum.PENDING, nullable=False, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resultados
    results_found = Column(Integer, default=0, nullable=False)
    results_saved = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    source = relationship("ScrapingSource", back_populates="scraping_jobs")
    user = relationship("User", back_populates="scraping_jobs")

    def __repr__(self):
        return f"<ScrapingJob(id={self.id}, source_id={self.source_id}, status='{self.status.value}')>"


# ==================== MODELOS DE HISTORIAL E INTERACCIONES ====================

class UserJobInteraction(Base):
    """
    Modelo para registrar interacciones entre usuarios y ofertas laborales.
    Permite tracking detallado del comportamiento del usuario.
    """
    __tablename__ = "user_job_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_offers.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # viewed, saved, applied, rejected
    
    # Metadatos adicionales en JSON
    interaction_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="job_interactions")
    job = relationship("JobOffer", back_populates="user_interactions")

    def __repr__(self):
        return f"<UserJobInteraction(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, action='{self.action}')>"


class SearchHistory(Base):
    """
    Modelo para historial de búsquedas de usuarios.
    Permite analisis de patrones de busqueda y recomendaciones.
    """
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    search_query = Column(String(500), nullable=False, index=True)
    filters_applied = Column(JSON, nullable=True, default={})  # Filtros aplicados en la busqueda
    results_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="search_history")

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, query='{self.search_query[:50]}')>"


# ==================== ÍNDICES ADICIONALES ====================
# Los indices se pueden crear mediante migraciones de Alembic para optimizar consultas frecuentes

# Indices compuestos sugeridos:
# - (user_id, created_at) en user_job_interactions para historial por usuario
# - (job_id, action) en user_job_interactions para estadisticas por oferta
# - (status, fecha_publicacion) en job_offers para busquedas activas
# - (empresa_id, status) en job_offers para ofertas por empresa
# - (source_id, status, created_at) en scraping_jobs para monitoreo