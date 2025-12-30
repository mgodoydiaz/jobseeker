# crud.py
# Operaciones CRUD (Create, Read, Update, Delete) para la base de datos
# Funciones para interactuar con los modelos de SQLAlchemy

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.database_models import (
    User, Company, JobOffer, ScrapingSource, ScrapingJob,
    UserJobInteraction, SearchHistory,
    JobStatusEnum, ApplicationStatusEnum, ScrapingStatusEnum, UserRoleEnum
)
from ..models.job_models import (
    UserCreate, UserUpdate, CompanyCreate, CompanyUpdate,
    JobOfferCreate, JobOfferUpdate, ScrapingSourceCreate, ScrapingSourceUpdate,
    ScrapingJobCreate, UserJobInteractionCreate, SearchHistoryCreate
)
from ..core.utils import hash_password


# ==================== CRUD PARA USUARIOS ====================

def create_user(db: Session, user: UserCreate) -> User:
    """Crear un nuevo usuario en la base de datos."""
    hashed_password = hash_password(user.password)
    db_user = User(
        nombre=user.nombre,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role if hasattr(user, 'role') else UserRoleEnum.USER,
        perfil_json=user.perfil_json if hasattr(user, 'perfil_json') else {}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Obtener un usuario por ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Obtener un usuario por email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtener lista de usuarios con paginación."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Actualizar un usuario existente."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = hash_password(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Eliminar un usuario (soft delete - marcar como inactivo)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    return True


def update_user_last_login(db: Session, user_id: int) -> None:
    """Actualizar la fecha de ultimo login del usuario."""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()


# ==================== CRUD PARA EMPRESAS ====================

def create_company(db: Session, company: CompanyCreate) -> Company:
    """Crear una nueva empresa."""
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_company(db: Session, company_id: int) -> Optional[Company]:
    """Obtener una empresa por ID."""
    return db.query(Company).filter(Company.id == company_id).first()


def get_company_by_name(db: Session, nombre: str) -> Optional[Company]:
    """Obtener una empresa por nombre."""
    return db.query(Company).filter(Company.nombre == nombre).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100, sector: Optional[str] = None) -> List[Company]:
    """Obtener lista de empresas con filtros opcionales."""
    query = db.query(Company)
    if sector:
        query = query.filter(Company.sector == sector)
    return query.offset(skip).limit(limit).all()


def update_company(db: Session, company_id: int, company_update: CompanyUpdate) -> Optional[Company]:
    """Actualizar una empresa existente."""
    db_company = get_company(db, company_id)
    if not db_company:
        return None
    
    update_data = company_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_company, field, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    """Eliminar una empresa."""
    db_company = get_company(db, company_id)
    if not db_company:
        return False
    
    db.delete(db_company)
    db.commit()
    return True


# ==================== CRUD PARA OFERTAS LABORALES ====================

def create_job_offer(db: Session, job: JobOfferCreate) -> JobOffer:
    """Crear una nueva oferta laboral."""
    db_job = JobOffer(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job_offer(db: Session, job_id: int) -> Optional[JobOffer]:
    """Obtener una oferta laboral por ID."""
    return db.query(JobOffer).filter(JobOffer.id == job_id).first()


def get_job_offer_by_url(db: Session, url: str) -> Optional[JobOffer]:
    """Obtener una oferta laboral por URL (para evitar duplicados)."""
    return db.query(JobOffer).filter(JobOffer.url == url).first()


def get_job_offers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    titulo: Optional[str] = None,
    ubicacion: Optional[str] = None,
    empresa_id: Optional[int] = None,
    status: Optional[JobStatusEnum] = None,
    modalidad: Optional[str] = None,
    nivel_experiencia: Optional[str] = None,
    salario_min: Optional[float] = None,
    salario_max: Optional[float] = None
) -> List[JobOffer]:
    """Obtener ofertas laborales con filtros avanzados."""
    query = db.query(JobOffer)
    
    # Aplicar filtros
    if titulo:
        query = query.filter(JobOffer.titulo.ilike(f"%{titulo}%"))
    if ubicacion:
        query = query.filter(JobOffer.ubicacion.ilike(f"%{ubicacion}%"))
    if empresa_id:
        query = query.filter(JobOffer.empresa_id == empresa_id)
    if status:
        query = query.filter(JobOffer.status == status)
    if modalidad:
        query = query.filter(JobOffer.modalidad == modalidad)
    if nivel_experiencia:
        query = query.filter(JobOffer.nivel_experiencia == nivel_experiencia)
    if salario_min:
        query = query.filter(JobOffer.salario >= salario_min)
    if salario_max:
        query = query.filter(JobOffer.salario <= salario_max)
    
    # Ordenar por fecha de publicacion (mas recientes primero)
    query = query.order_by(desc(JobOffer.fecha_publicacion))
    
    return query.offset(skip).limit(limit).all()


def update_job_offer(db: Session, job_id: int, job_update: JobOfferUpdate) -> Optional[JobOffer]:
    """Actualizar una oferta laboral existente."""
    db_job = get_job_offer(db, job_id)
    if not db_job:
        return None
    
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job_offer(db: Session, job_id: int) -> bool:
    """Eliminar una oferta laboral."""
    db_job = get_job_offer(db, job_id)
    if not db_job:
        return False
    
    db.delete(db_job)
    db.commit()
    return True


def search_job_offers(
    db: Session,
    search_query: str,
    skip: int = 0,
    limit: int = 100
) -> List[JobOffer]:
    """Busqueda de texto completo en ofertas laborales."""
    query = db.query(JobOffer).filter(
        or_(
            JobOffer.titulo.ilike(f"%{search_query}%"),
            JobOffer.descripcion.ilike(f"%{search_query}%")
        )
    ).order_by(desc(JobOffer.fecha_publicacion))
    
    return query.offset(skip).limit(limit).all()


# ==================== CRUD PARA FUENTES DE SCRAPING ====================

def create_scraping_source(db: Session, source: ScrapingSourceCreate) -> ScrapingSource:
    """Crear una nueva fuente de scraping."""
    db_source = ScrapingSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def get_scraping_source(db: Session, source_id: int) -> Optional[ScrapingSource]:
    """Obtener una fuente de scraping por ID."""
    return db.query(ScrapingSource).filter(ScrapingSource.id == source_id).first()


def get_scraping_sources(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[ScrapingSource]:
    """Obtener fuentes de scraping con filtros."""
    query = db.query(ScrapingSource)
    if is_active is not None:
        query = query.filter(ScrapingSource.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_scraping_source(db: Session, source_id: int, source_update: ScrapingSourceUpdate) -> Optional[ScrapingSource]:
    """Actualizar una fuente de scraping."""
    db_source = get_scraping_source(db, source_id)
    if not db_source:
        return None
    
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source


# ==================== CRUD PARA TRABAJOS DE SCRAPING ====================

def create_scraping_job(db: Session, scraping_job: ScrapingJobCreate, user_id: Optional[int] = None) -> ScrapingJob:
    """Crear un nuevo trabajo de scraping."""
    db_scraping_job = ScrapingJob(**scraping_job.dict(), user_id=user_id)
    db.add(db_scraping_job)
    db.commit()
    db.refresh(db_scraping_job)
    return db_scraping_job


def get_scraping_job(db: Session, job_id: int) -> Optional[ScrapingJob]:
    """Obtener un trabajo de scraping por ID."""
    return db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()


def get_scraping_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[ScrapingStatusEnum] = None,
    user_id: Optional[int] = None
) -> List[ScrapingJob]:
    """Obtener trabajos de scraping con filtros."""
    query = db.query(ScrapingJob)
    if status:
        query = query.filter(ScrapingJob.status == status)
    if user_id:
        query = query.filter(ScrapingJob.user_id == user_id)
    
    return query.order_by(desc(ScrapingJob.created_at)).offset(skip).limit(limit).all()


def update_scraping_job_status(
    db: Session,
    job_id: int,
    status: ScrapingStatusEnum,
    results_found: Optional[int] = None,
    results_saved: Optional[int] = None,
    error_message: Optional[str] = None
) -> Optional[ScrapingJob]:
    """Actualizar el estado de un trabajo de scraping."""
    db_job = get_scraping_job(db, job_id)
    if not db_job:
        return None
    
    db_job.status = status
    if status == ScrapingStatusEnum.RUNNING and not db_job.started_at:
        db_job.started_at = datetime.utcnow()
    elif status in [ScrapingStatusEnum.COMPLETED, ScrapingStatusEnum.FAILED]:
        db_job.completed_at = datetime.utcnow()
    
    if results_found is not None:
        db_job.results_found = results_found
    if results_saved is not None:
        db_job.results_saved = results_saved
    if error_message is not None:
        db_job.error_message = error_message
    
    db.commit()
    db.refresh(db_job)
    return db_job


# ==================== CRUD PARA INTERACCIONES DE USUARIO ====================

def create_user_job_interaction(db: Session, interaction: UserJobInteractionCreate) -> UserJobInteraction:
    """Crear una nueva interaccion usuario-oferta."""
    db_interaction = UserJobInteraction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def get_user_job_interactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None
) -> List[UserJobInteraction]:
    """Obtener interacciones de un usuario."""
    query = db.query(UserJobInteraction).filter(UserJobInteraction.user_id == user_id)
    if action:
        query = query.filter(UserJobInteraction.action == action)
    
    return query.order_by(desc(UserJobInteraction.created_at)).offset(skip).limit(limit).all()


# ==================== CRUD PARA HISTORIAL DE BÚSQUEDAS ====================

def create_search_history(db: Session, search: SearchHistoryCreate) -> SearchHistory:
    """Crear un registro de historial de busqueda."""
    db_search = SearchHistory(**search.dict())
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return db_search


def get_user_search_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[SearchHistory]:
    """Obtener historial de busquedas de un usuario."""
    return db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(desc(SearchHistory.created_at)).offset(skip).limit(limit).all()


# ==================== FUNCIONES DE ESTADÍSTICAS ====================

def get_job_stats(db: Session) -> Dict[str, Any]:
    """Obtener estadisticas generales de ofertas laborales."""
    total_jobs = db.query(JobOffer).count()
    active_jobs = db.query(JobOffer).filter(JobOffer.status == JobStatusEnum.ACTIVE).count()
    companies_count = db.query(Company).count()
    
    # Ofertas por modalidad
    modalidad_stats = db.query(
        JobOffer.modalidad,
        func.count(JobOffer.id).label('count')
    ).group_by(JobOffer.modalidad).all()
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "companies_count": companies_count,
        "modalidad_distribution": {stat.modalidad: stat.count for stat in modalidad_stats}
    }


def get_scraping_stats(db: Session) -> Dict[str, Any]:
    """Obtener estadisticas de scraping."""
    total_sources = db.query(ScrapingSource).count()
    active_sources = db.query(ScrapingSource).filter(ScrapingSource.is_active == True).count()
    total_scraping_jobs = db.query(ScrapingJob).count()
    
    # Trabajos por estado
    status_stats = db.query(
        ScrapingJob.status,
        func.count(ScrapingJob.id).label('count')
    ).group_by(ScrapingJob.status).all()
    
    return {
        "total_sources": total_sources,
        "active_sources": active_sources,
        "total_scraping_jobs": total_scraping_jobs,
        "status_distribution": {stat.status.value: stat.count for stat in status_stats}
    }