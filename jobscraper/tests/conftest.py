# conftest.py
# Configuración global de pytest y fixtures compartidas
# IMPLEMENTADO: Fixtures avanzadas para testing con datos de prueba

import pytest
from typing import Generator, Dict, Any
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from ..app.models.database_models import User, Company, JobOffer, ScrapingSource
from ..app.models.job_models import UserCreate, CompanyCreate, JobOfferCreate
from ..app.database import crud
from ..app.core.utils import hash_password, create_access_token


# ==================== FIXTURES DE DATOS DE PRUEBA ====================

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """
    Datos de ejemplo para crear un usuario.
    """
    return {
        "nombre": "Juan Pérez",
        "email": "juan.perez@example.com",
        "password": "TestPassword123!",
        "perfil_json": {
            "habilidades": ["Python", "FastAPI", "PostgreSQL"],
            "experiencia_anos": 5,
            "ubicacion_preferida": ["Madrid", "Barcelona"]
        }
    }


@pytest.fixture
def sample_company_data() -> Dict[str, Any]:
    """
    Datos de ejemplo para crear una empresa.
    """
    return {
        "nombre": "TechCorp Solutions",
        "sector": "Tecnología",
        "sitio_web": "https://techcorp.example.com",
        "descripcion": "Empresa líder en desarrollo de software",
        "tamano": "mediana",
        "ubicacion": "Madrid, España"
    }


@pytest.fixture
def sample_job_offer_data() -> Dict[str, Any]:
    """
    Datos de ejemplo para crear una oferta laboral.
    """
    return {
        "titulo": "Desarrollador Python Senior",
        "descripcion": "Buscamos desarrollador Python con experiencia en FastAPI",
        "ubicacion": "Madrid",
        "salario": 55000.00,
        "url": "https://example.com/job/python-developer",
        "requisitos": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "beneficios": ["Trabajo remoto", "Seguro médico", "Formación continua"],
        "modalidad": "híbrido",
        "tipo_contrato": "indefinido",
        "nivel_experiencia": "senior"
    }


@pytest.fixture
def sample_scraping_source_data() -> Dict[str, Any]:
    """
    Datos de ejemplo para crear una fuente de scraping.
    """
    return {
        "nombre": "LinkedIn Jobs",
        "base_url": "https://linkedin.com/jobs",
        "descripcion": "Portal de empleos de LinkedIn",
        "selectors": {
            "title": ".job-title",
            "company": ".company-name",
            "location": ".job-location",
            "salary": ".salary-range"
        },
        "headers": {
            "User-Agent": "JobScraper-Bot/1.0"
        },
        "delay_seconds": 2.0,
        "max_pages": 10
    }


# ==================== FIXTURES DE OBJETOS CREADOS ====================

@pytest.fixture
def created_user(db: Session, sample_user_data: Dict[str, Any]) -> User:
    """
    Crea un usuario en la base de datos de prueba.
    """
    user_create = UserCreate(**sample_user_data)
    hashed_password = hash_password(sample_user_data["password"])
    return crud.create_user(db, user_create, hashed_password)


@pytest.fixture
def created_company(db: Session, sample_company_data: Dict[str, Any]) -> Company:
    """
    Crea una empresa en la base de datos de prueba.
    """
    company_create = CompanyCreate(**sample_company_data)
    return crud.create_company(db, company_create)


@pytest.fixture
def created_job_offer(db: Session, created_company: Company, sample_job_offer_data: Dict[str, Any]) -> JobOffer:
    """
    Crea una oferta laboral en la base de datos de prueba.
    """
    job_data = sample_job_offer_data.copy()
    job_data["empresa_id"] = created_company.id
    job_create = JobOfferCreate(**job_data)
    return crud.create_job_offer(db, job_create)


@pytest.fixture
def created_scraping_source(db: Session, sample_scraping_source_data: Dict[str, Any]) -> ScrapingSource:
    """
    Crea una fuente de scraping en la base de datos de prueba.
    """
    from ..app.models.job_models import ScrapingSourceCreate
    source_create = ScrapingSourceCreate(**sample_scraping_source_data)
    return crud.create_scraping_source(db, source_create)


# ==================== FIXTURES DE AUTENTICACIÓN ====================

@pytest.fixture
def auth_headers(created_user: User) -> Dict[str, str]:
    """
    Headers de autenticación con token JWT válido.
    """
    token_data = {"sub": str(created_user.id), "email": created_user.email}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_user(db: Session, sample_user_data: Dict[str, Any]) -> User:
    """
    Crea un usuario administrador.
    """
    admin_data = sample_user_data.copy()
    admin_data["email"] = "admin@example.com"
    admin_data["nombre"] = "Admin User"
    
    user_create = UserCreate(**admin_data)
    hashed_password = hash_password(admin_data["password"])
    user = crud.create_user(db, user_create, hashed_password)
    
    # Cambiar rol a admin
    from ..app.models.database_models import UserRoleEnum
    user.role = UserRoleEnum.ADMIN
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def admin_headers(admin_user: User) -> Dict[str, str]:
    """
    Headers de autenticación para usuario administrador.
    """
    token_data = {"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


# ==================== FIXTURES DE DATOS MÚLTIPLES ====================

@pytest.fixture
def multiple_companies(db: Session) -> list[Company]:
    """
    Crea múltiples empresas para pruebas de listado.
    """
    companies_data = [
        {
            "nombre": "TechCorp",
            "sector": "Tecnología",
            "sitio_web": "https://techcorp.com"
        },
        {
            "nombre": "DataSoft",
            "sector": "Software",
            "sitio_web": "https://datasoft.com"
        },
        {
            "nombre": "AI Solutions",
            "sector": "Inteligencia Artificial",
            "sitio_web": "https://aisolutions.com"
        }
    ]
    
    companies = []
    for company_data in companies_data:
        company_create = CompanyCreate(**company_data)
        company = crud.create_company(db, company_create)
        companies.append(company)
    
    return companies


@pytest.fixture
def multiple_job_offers(db: Session, multiple_companies: list[Company]) -> list[JobOffer]:
    """
    Crea múltiples ofertas laborales para pruebas de búsqueda.
    """
    jobs_data = [
        {
            "titulo": "Desarrollador Python",
            "descripcion": "Desarrollo backend con Python",
            "ubicacion": "Madrid",
            "salario": 45000.00,
            "url": "https://example.com/job/1",
            "modalidad": "remoto",
            "nivel_experiencia": "junior"
        },
        {
            "titulo": "Data Scientist",
            "descripcion": "Análisis de datos con Python",
            "ubicacion": "Barcelona",
            "salario": 60000.00,
            "url": "https://example.com/job/2",
            "modalidad": "presencial",
            "nivel_experiencia": "senior"
        },
        {
            "titulo": "DevOps Engineer",
            "descripcion": "Infraestructura y deployment",
            "ubicacion": "Valencia",
            "salario": 55000.00,
            "url": "https://example.com/job/3",
            "modalidad": "híbrido",
            "nivel_experiencia": "mid"
        }
    ]
    
    jobs = []
    for i, job_data in enumerate(jobs_data):
        job_data["empresa_id"] = multiple_companies[i].id
        job_create = JobOfferCreate(**job_data)
        job = crud.create_job_offer(db, job_create)
        jobs.append(job)
    
    return jobs


# ==================== FIXTURES DE CONFIGURACIÓN ====================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Configuración automática del entorno de pruebas.
    """
    # Configurar variables de entorno para pruebas
    import os
    os.environ["DEBUG"] = "True"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Limpiar después de las pruebas
    # Aquí se pueden agregar tareas de limpieza adicionales


@pytest.fixture
def mock_datetime():
    """
    Mock de datetime para pruebas determinísticas.
    """
    from unittest.mock import patch
    fixed_datetime = datetime(2024, 1, 15, 10, 30, 0)
    
    with patch('datetime.datetime') as mock_dt:
        mock_dt.utcnow.return_value = fixed_datetime
        mock_dt.now.return_value = fixed_datetime
        yield mock_dt