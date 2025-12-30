# routes.py
# Definición de rutas y endpoints de la API
# Aquí se configurarán los endpoints para gestionar ofertas laborales
# IMPLEMENTADO: Todos los endpoints de la API REST con autenticación JWT

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from ..database.connection import get_db
from ..database import crud
from ..models.job_models import (
    # Auth
    LoginRequest, Token, UserCreate, UserResponse,
    # Users
    UserUpdate, UserProfile,
    # Companies
    CompanyCreate, CompanyUpdate, CompanyResponse,
    # Jobs
    JobOfferCreate, JobOfferUpdate, JobOfferResponse, JobOfferList,
    JobSearchFilters, PaginationParams,
    # Scraping
    ScrapingSourceCreate, ScrapingSourceUpdate, ScrapingSourceResponse,
    ScrapingJobCreate, ScrapingJobResponse,
    # Interactions
    UserJobInteractionCreate, UserJobInteractionResponse,
    SearchHistoryCreate, SearchHistoryResponse
)
from ..core.utils import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token, log_user_action, calculate_pagination
)

# Configurar seguridad JWT
security = HTTPBearer()

# Crear router principal
router = APIRouter()


# ==================== DEPENDENCIAS DE AUTENTICACIÓN ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Obtiene el usuario actual desde el token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = crud.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Verifica que el usuario actual esté activo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@router.post("/auth/register", response_model=UserResponse, tags=["Autenticación"])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    """
    # Verificar si el email ya existe
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear usuario con contraseña hasheada
    db_user = crud.create_user(db=db, user=user)
    
    log_user_action(db_user.id, "user_registered")
    
    return db_user


@router.post("/auth/login", response_model=Token, tags=["Autenticación"])
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna tokens JWT.
    """
    # Verificar credenciales
    user = crud.get_user_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Actualizar último login
    crud.update_user_last_login(db, user.id)
    
    log_user_action(user.id, "user_login")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutos
    }


@router.get("/auth/me", response_model=UserResponse, tags=["Autenticación"])
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Obtiene información del usuario autenticado.
    """
    return current_user


# ==================== ENDPOINTS DE USUARIOS ====================

@router.get("/users", response_model=List[UserResponse], tags=["Usuarios"])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de usuarios (solo para administradores).
    """
    # Solo admins pueden ver lista de usuarios
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    users = crud.get_users(db, skip=skip, limit=limit, is_active=is_active)
    return users


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Usuarios"])
async def get_user(
    user_id: int = Path(..., gt=0),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene información de un usuario específico.
    """
    # Solo el propio usuario o admin puede ver la información
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Usuarios"])
async def update_user(
    user_id: int = Path(..., gt=0),
    user_update: UserUpdate = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza información de un usuario.
    """
    # Solo el propio usuario o admin puede actualizar
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    
    user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    log_user_action(current_user.id, "user_updated", {"target_user_id": user_id})
    
    return user


@router.get("/users/{user_id}/stats", tags=["Usuarios"])
async def get_user_stats(
    user_id: int = Path(..., gt=0),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de un usuario.
    """
    # Solo el propio usuario o admin puede ver estadísticas
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    stats = crud.get_user_stats(db, user_id=user_id)
    return stats


# ==================== ENDPOINTS DE EMPRESAS ====================

@router.post("/companies", response_model=CompanyResponse, tags=["Empresas"])
async def create_company(
    company: CompanyCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva empresa.
    """
    # Verificar si ya existe una empresa con el mismo nombre
    existing_company = crud.get_company_by_name(db, name=company.nombre)
    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una empresa con ese nombre"
        )
    
    db_company = crud.create_company(db=db, company=company)
    
    log_user_action(current_user.id, "company_created", {"company_id": db_company.id})
    
    return db_company


@router.get("/companies", response_model=List[CompanyResponse], tags=["Empresas"])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sector: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de empresas con filtros opcionales.
    """
    companies = crud.get_companies(db, skip=skip, limit=limit, sector=sector, search=search)
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse, tags=["Empresas"])
async def get_company(
    company_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """
    Obtiene información de una empresa específica.
    """
    company = crud.get_company(db, company_id=company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return company


@router.put("/companies/{company_id}", response_model=CompanyResponse, tags=["Empresas"])
async def update_company(
    company_id: int = Path(..., gt=0),
    company_update: CompanyUpdate = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza información de una empresa.
    """
    company = crud.update_company(db, company_id=company_id, company_update=company_update)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    log_user_action(current_user.id, "company_updated", {"company_id": company_id})
    
    return company


# ==================== ENDPOINTS DE OFERTAS LABORALES ====================

@router.post("/jobs", response_model=JobOfferResponse, tags=["Ofertas Laborales"])
async def create_job_offer(
    job_offer: JobOfferCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva oferta laboral.
    """
    # Verificar que la empresa existe
    company = crud.get_company(db, company_id=job_offer.empresa_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    db_job = crud.create_job_offer(db=db, job_offer=job_offer)
    
    log_user_action(current_user.id, "job_created", {"job_id": db_job.id})
    
    return db_job


@router.get("/jobs", response_model=JobOfferList, tags=["Ofertas Laborales"])
async def search_job_offers(
    # Parámetros de paginación
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|fecha_publicacion|salario|titulo)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    
    # Filtros de búsqueda
    search_query: Optional[str] = Query(None),
    ubicacion: Optional[List[str]] = Query(None),
    salario_min: Optional[float] = Query(None, ge=0),
    salario_max: Optional[float] = Query(None, ge=0),
    modalidad: Optional[List[str]] = Query(None),
    tipo_contrato: Optional[List[str]] = Query(None),
    nivel_experiencia: Optional[List[str]] = Query(None),
    empresa_ids: Optional[List[int]] = Query(None),
    solo_activas: bool = Query(True),
    
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Busca ofertas laborales con filtros avanzados y paginación.
    """
    # Crear objetos de filtros y paginación
    pagination = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    filters = JobSearchFilters(
        search_query=search_query,
        ubicacion=ubicacion,
        salario_min=salario_min,
        salario_max=salario_max,
        modalidad=modalidad,
        tipo_contrato=tipo_contrato,
        nivel_experiencia=nivel_experiencia,
        empresa_ids=empresa_ids,
        solo_activas=solo_activas
    )
    
    # Realizar búsqueda
    job_offers, total_count = crud.get_job_offers(db, pagination=pagination, filters=filters)
    
    # Registrar búsqueda en historial
    if search_query:
        search_history = SearchHistoryCreate(
            user_id=current_user.id,
            search_query=search_query,
            filters_applied=filters.dict(exclude_unset=True),
            results_count=total_count
        )
        crud.create_search_history(db, search=search_history)
    
    # Calcular información de paginación
    total_pages = (total_count + size - 1) // size
    
    return JobOfferList(
        items=job_offers,
        total=total_count,
        page=page,
        size=size,
        pages=total_pages
    )


@router.get("/jobs/{job_id}", response_model=JobOfferResponse, tags=["Ofertas Laborales"])
async def get_job_offer(
    job_id: int = Path(..., gt=0),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene información detallada de una oferta laboral.
    """
    job_offer = crud.get_job_offer(db, job_id=job_id)
    if job_offer is None:
        raise HTTPException(status_code=404, detail="Oferta laboral no encontrada")
    
    # Registrar interacción de visualización
    interaction = UserJobInteractionCreate(
        user_id=current_user.id,
        job_id=job_id,
        action="viewed"
    )
    crud.create_user_job_interaction(db, interaction=interaction)
    
    return job_offer


@router.put("/jobs/{job_id}", response_model=JobOfferResponse, tags=["Ofertas Laborales"])
async def update_job_offer(
    job_id: int = Path(..., gt=0),
    job_update: JobOfferUpdate = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza una oferta laboral.
    """
    job_offer = crud.update_job_offer(db, job_id=job_id, job_update=job_update)
    if job_offer is None:
        raise HTTPException(status_code=404, detail="Oferta laboral no encontrada")
    
    log_user_action(current_user.id, "job_updated", {"job_id": job_id})
    
    return job_offer


@router.delete("/jobs/{job_id}", tags=["Ofertas Laborales"])
async def delete_job_offer(
    job_id: int = Path(..., gt=0),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una oferta laboral.
    """
    # Solo admins pueden eliminar ofertas
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    
    success = crud.delete_job_offer(db, job_id=job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Oferta laboral no encontrada")
    
    log_user_action(current_user.id, "job_deleted", {"job_id": job_id})
    
    return {"message": "Oferta laboral eliminada correctamente"}


@router.get("/jobs/recent", response_model=List[JobOfferResponse], tags=["Ofertas Laborales"])
async def get_recent_job_offers(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtiene ofertas laborales recientes.
    """
    job_offers = crud.get_recent_job_offers(db, days=days, limit=limit)
    return job_offers


# ==================== ENDPOINTS DE INTERACCIONES ====================

@router.post("/jobs/{job_id}/interact", response_model=UserJobInteractionResponse, tags=["Interacciones"])
async def create_job_interaction(
    job_id: int = Path(..., gt=0),
    action: str = Query(..., regex="^(saved|applied|rejected|interested)$"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Registra una interacción del usuario con una oferta laboral.
    """
    # Verificar que la oferta existe
    job_offer = crud.get_job_offer(db, job_id=job_id)
    if not job_offer:
        raise HTTPException(status_code=404, detail="Oferta laboral no encontrada")
    
    interaction = UserJobInteractionCreate(
        user_id=current_user.id,
        job_id=job_id,
        action=action
    )
    
    db_interaction = crud.create_user_job_interaction(db, interaction=interaction)
    
    log_user_action(current_user.id, f"job_{action}", {"job_id": job_id})
    
    return db_interaction


@router.get("/users/{user_id}/interactions", response_model=List[UserJobInteractionResponse], tags=["Interacciones"])
async def get_user_interactions(
    user_id: int = Path(..., gt=0),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de interacciones de un usuario.
    """
    # Solo el propio usuario o admin puede ver las interacciones
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    interactions = crud.get_user_interactions(db, user_id=user_id, action=action, skip=skip, limit=limit)
    return interactions


# ==================== ENDPOINTS DE SCRAPING ====================

@router.post("/scraping/sources", response_model=ScrapingSourceResponse, tags=["Scraping"])
async def create_scraping_source(
    source: ScrapingSourceCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva fuente de scraping.
    """
    # Solo admins pueden crear fuentes de scraping
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    
    db_source = crud.create_scraping_source(db=db, source=source)
    
    log_user_action(current_user.id, "scraping_source_created", {"source_id": db_source.id})
    
    return db_source


@router.get("/scraping/sources", response_model=List[ScrapingSourceResponse], tags=["Scraping"])
async def get_scraping_sources(
    is_active: Optional[bool] = Query(None),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de fuentes de scraping.
    """
    sources = crud.get_scraping_sources(db, is_active=is_active)
    return sources


@router.post("/scraping/jobs", response_model=ScrapingJobResponse, tags=["Scraping"])
async def create_scraping_job(
    scraping_job: ScrapingJobCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo trabajo de scraping.
    """
    # Verificar que la fuente existe
    source = crud.get_scraping_source(db, source_id=scraping_job.source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de scraping no encontrada")
    
    # Agregar usuario actual al trabajo
    scraping_job.user_id = current_user.id
    
    db_job = crud.create_scraping_job(db=db, scraping_job=scraping_job)
    
    log_user_action(current_user.id, "scraping_job_created", {"scraping_job_id": db_job.id})
    
    return db_job


@router.get("/scraping/jobs", response_model=List[ScrapingJobResponse], tags=["Scraping"])
async def get_scraping_jobs(
    status: Optional[str] = Query(None),
    source_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de trabajos de scraping.
    """
    # Los usuarios normales solo ven sus propios trabajos
    user_id = None if current_user.role.value == "admin" else current_user.id
    
    jobs = crud.get_scraping_jobs(
        db, 
        status=status, 
        source_id=source_id, 
        user_id=user_id,
        skip=skip, 
        limit=limit
    )
    return jobs


# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@router.get("/stats/platform", tags=["Estadísticas"])
async def get_platform_stats(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas generales de la plataforma.
    """
    # Solo admins pueden ver estadísticas de la plataforma
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    stats = crud.get_platform_stats(db)
    return stats


@router.get("/stats/popular-searches", tags=["Estadísticas"])
async def get_popular_searches(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las búsquedas más populares.
    """
    # Solo admins pueden ver búsquedas populares
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    popular_searches = crud.get_popular_searches(db, days=days, limit=limit)
    
    return {
        "popular_searches": [
            {"query": query, "count": count} 
            for query, count in popular_searches
        ],
        "period_days": days
    }


# ==================== ENDPOINT RAÍZ DE API V1 ====================

@router.get("/", tags=["API v1"])
async def api_root():
    """
    Endpoint raíz de la API v1.
    Retorna información sobre todos los endpoints disponibles.
    """
    return {
        "message": "JobScraper API v1",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "users": {
                "list": "GET /users",
                "get": "GET /users/{user_id}",
                "update": "PUT /users/{user_id}",
                "stats": "GET /users/{user_id}/stats",
                "interactions": "GET /users/{user_id}/interactions"
            },
            "companies": {
                "create": "POST /companies",
                "list": "GET /companies",
                "get": "GET /companies/{company_id}",
                "update": "PUT /companies/{company_id}"
            },
            "jobs": {
                "create": "POST /jobs",
                "search": "GET /jobs",
                "get": "GET /jobs/{job_id}",
                "update": "PUT /jobs/{job_id}",
                "delete": "DELETE /jobs/{job_id}",
                "recent": "GET /jobs/recent",
                "interact": "POST /jobs/{job_id}/interact"
            },
            "scraping": {
                "create_source": "POST /scraping/sources",
                "list_sources": "GET /scraping/sources",
                "create_job": "POST /scraping/jobs",
                "list_jobs": "GET /scraping/jobs"
            },
            "stats": {
                "platform": "GET /stats/platform",
                "popular_searches": "GET /stats/popular-searches"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/api/v1/openapi.json"
        }
    }