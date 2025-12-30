# job_models.py
# Modelos de datos para ofertas laborales
# Definición de esquemas Pydantic para validación y serialización de datos

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, HttpUrl, validator, Field
from typing import Optional, List, Dict, Any, Union
# ==================== ENUMS ====================

class JobStatus(str, Enum):
    """Estados de las ofertas laborales"""
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    DRAFT = "draft"


class ApplicationStatus(str, Enum):
    """Estados de postulaciones"""
    PENDING = "pending"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class ScrapingStatus(str, Enum):
    """Estados del proceso de scraping"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class UserRole(str, Enum):
    """Roles de usuario"""
    USER = "user"
    ADMIN = "admin"
    SCRAPER = "scraper"


# ==================== ESQUEMAS BASE ====================

class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp"""
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== ESQUEMAS DE USUARIO ====================

class UserBase(BaseModel):
    """Esquema base para usuario"""
    nombre: str = Field(..., min_length=2, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    perfil_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe tener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    perfil_json: Optional[Dict[str, Any]] = None


class UserResponse(UserBase, TimestampMixin):
    """Esquema de respuesta para usuario"""
    id: int
    role: UserRole = UserRole.USER
    is_active: bool = True
    perfil_json: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    """Esquema detallado del perfil de usuario"""
    habilidades: List[str] = Field(default_factory=list)
    experiencia_anos: Optional[int] = Field(None, ge=0, le=50)
    nivel_educacion: Optional[str] = None
    ubicacion_preferida: List[str] = Field(default_factory=list)
    salario_minimo: Optional[Decimal] = Field(None, ge=0)
    salario_maximo: Optional[Decimal] = Field(None, ge=0)
    modalidad_trabajo: List[str] = Field(default_factory=list)  # remoto, presencial, híbrido
    sectores_interes: List[str] = Field(default_factory=list)
    idiomas: Dict[str, str] = Field(default_factory=dict)  # {"español": "nativo", "inglés": "avanzado"}
    cv_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    
    @validator('salario_maximo')
    def validate_salario_range(cls, v, values):
        if v is not None and 'salario_minimo' in values and values['salario_minimo'] is not None:
            if v < values['salario_minimo']:
                raise ValueError('El salario máximo debe ser mayor al mínimo')
        return v


# ==================== ESQUEMAS DE EMPRESA ====================

class CompanyBase(BaseModel):
    """Esquema base para empresa"""
    nombre: str = Field(..., min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    sitio_web: Optional[HttpUrl] = None


class CompanyCreate(CompanyBase):
    """Esquema para crear empresa"""
    descripcion: Optional[str] = None
    tamano: Optional[str] = None  # startup, pequeña, mediana, grande
    ubicacion: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Esquema para actualizar empresa"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    sitio_web: Optional[HttpUrl] = None
    descripcion: Optional[str] = None
    tamano: Optional[str] = None
    ubicacion: Optional[str] = None


class CompanyResponse(CompanyBase, TimestampMixin):
    """Esquema de respuesta para empresa"""
    id: int
    descripcion: Optional[str] = None
    tamano: Optional[str] = None
    ubicacion: Optional[str] = None
    total_ofertas: int = 0
    
    class Config:
        orm_mode = True


# ==================== ESQUEMAS DE OFERTA LABORAL ====================

class JobOfferBase(BaseModel):
    """Esquema base para oferta laboral"""
    titulo: str = Field(..., min_length=5, max_length=255)
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = Field(None, max_length=255)
    salario: Optional[Decimal] = Field(None, ge=0)
    url: HttpUrl


class JobOfferCreate(JobOfferBase):
    """Esquema para crear oferta laboral"""
    empresa_id: int = Field(..., gt=0)
    fecha_publicacion: Optional[datetime] = None
    requisitos: List[str] = Field(default_factory=list)
    beneficios: List[str] = Field(default_factory=list)
    modalidad: Optional[str] = None  # remoto, presencial, híbrido
    tipo_contrato: Optional[str] = None  # indefinido, temporal, freelance
    nivel_experiencia: Optional[str] = None  # junior, mid, senior
    
    @validator('titulo')
    def validate_titulo(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip().title()


class JobOfferUpdate(BaseModel):
    """Esquema para actualizar oferta laboral"""
    titulo: Optional[str] = Field(None, min_length=5, max_length=255)
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = Field(None, max_length=255)
    salario: Optional[Decimal] = Field(None, ge=0)
    status: Optional[JobStatus] = None
    requisitos: Optional[List[str]] = None
    beneficios: Optional[List[str]] = None
    modalidad: Optional[str] = None
    tipo_contrato: Optional[str] = None
    nivel_experiencia: Optional[str] = None


class JobOfferResponse(JobOfferBase, TimestampMixin):
    """Esquema de respuesta para oferta laboral"""
    id: int
    empresa_id: int
    fecha_publicacion: Optional[datetime] = None
    fecha_scrapeo: datetime
    status: JobStatus = JobStatus.ACTIVE
    requisitos: List[str] = Field(default_factory=list)
    beneficios: List[str] = Field(default_factory=list)
    modalidad: Optional[str] = None
    tipo_contrato: Optional[str] = None
    nivel_experiencia: Optional[str] = None
    empresa: CompanyResponse
    match_score: Optional[float] = None  # Puntuación de compatibilidad con usuario
    
    class Config:
        orm_mode = True


class JobOfferList(BaseModel):
    """Esquema para lista paginada de ofertas"""
    items: List[JobOfferResponse]
    total: int
    page: int
    size: int
    pages: int


# ==================== ESQUEMAS DE SCRAPING ====================

class ScrapingSourceBase(BaseModel):
    """Esquema base para fuentes de scraping"""
    nombre: str = Field(..., min_length=1, max_length=100)
    base_url: HttpUrl
    is_active: bool = True


class ScrapingSourceCreate(ScrapingSourceBase):
    """Esquema para crear fuente de scraping"""
    descripcion: Optional[str] = None
    selectors: Dict[str, str] = Field(default_factory=dict)  # CSS selectors
    headers: Dict[str, str] = Field(default_factory=dict)
    delay_seconds: float = Field(1.0, ge=0.1, le=10.0)
    max_pages: int = Field(10, ge=1, le=100)


class ScrapingSourceUpdate(BaseModel):
    """Esquema para actualizar fuente de scraping"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    base_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    descripcion: Optional[str] = None
    selectors: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    delay_seconds: Optional[float] = Field(None, ge=0.1, le=10.0)
    max_pages: Optional[int] = Field(None, ge=1, le=100)


class ScrapingSourceResponse(ScrapingSourceBase, TimestampMixin):
    """Esquema de respuesta para fuente de scraping"""
    id: int
    descripcion: Optional[str] = None
    selectors: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    delay_seconds: float = 1.0
    max_pages: int = 10
    total_jobs_scraped: int = 0
    last_scrape_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class ScrapingJobBase(BaseModel):
    """Esquema base para trabajo de scraping"""
    source_id: int = Field(..., gt=0)
    user_id: Optional[int] = Field(None, gt=0)
    search_terms: List[str] = Field(default_factory=list)
    location_filters: List[str] = Field(default_factory=list)


class ScrapingJobCreate(ScrapingJobBase):
    """Esquema para crear trabajo de scraping"""
    scheduled_at: Optional[datetime] = None
    max_results: int = Field(100, ge=1, le=1000)


class ScrapingJobResponse(ScrapingJobBase, TimestampMixin):
    """Esquema de respuesta para trabajo de scraping"""
    id: int
    status: ScrapingStatus = ScrapingStatus.PENDING
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    max_results: int = 100
    results_found: int = 0
    results_saved: int = 0
    error_message: Optional[str] = None
    source: ScrapingSourceResponse
    
    class Config:
        orm_mode = True


# ==================== ESQUEMAS DE HISTORIAL ====================

class UserJobInteractionBase(BaseModel):
    """Esquema base para interacciones usuario-oferta"""
    user_id: int = Field(..., gt=0)
    job_id: int = Field(..., gt=0)
    action: str = Field(..., min_length=1)  # viewed, saved, applied, rejected


class UserJobInteractionCreate(UserJobInteractionBase):
    """Esquema para crear interacción"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserJobInteractionResponse(UserJobInteractionBase, TimestampMixin):
    """Esquema de respuesta para interacción"""
    id: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    job: JobOfferResponse
    
    class Config:
        orm_mode = True


class SearchHistoryBase(BaseModel):
    """Esquema base para historial de búsquedas"""
    user_id: int = Field(..., gt=0)
    search_query: str = Field(..., min_length=1)
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class SearchHistoryCreate(SearchHistoryBase):
    """Esquema para crear historial de búsqueda"""
    results_count: int = Field(0, ge=0)


class SearchHistoryResponse(SearchHistoryBase, TimestampMixin):
    """Esquema de respuesta para historial de búsqueda"""
    id: int
    results_count: int = 0
    
    class Config:
        orm_mode = True


# ==================== ESQUEMAS DE FILTROS Y BÚSQUEDA ====================

class JobSearchFilters(BaseModel):
    """Filtros para búsqueda de ofertas"""
    search_query: Optional[str] = None
    ubicacion: Optional[List[str]] = None
    salario_min: Optional[Decimal] = Field(None, ge=0)
    salario_max: Optional[Decimal] = Field(None, ge=0)
    modalidad: Optional[List[str]] = None
    tipo_contrato: Optional[List[str]] = None
    nivel_experiencia: Optional[List[str]] = None
    empresa_ids: Optional[List[int]] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    solo_activas: bool = True


class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", regex="^(created_at|fecha_publicacion|salario|titulo)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


# ==================== ESQUEMAS DE AUTENTICACIÓN ====================

class Token(BaseModel):
    """Esquema para token de acceso"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Datos del token"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Esquema para login"""
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """Esquema para reset de contraseña"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Esquema para confirmar reset de contraseña"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)