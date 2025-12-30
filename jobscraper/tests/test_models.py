# test_models.py
# Tests unitarios para modelos Pydantic y ORM
# Validación de esquemas, relaciones y constraints de base de datos

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from ..app.models.database_models import (
    User, Company, JobOffer, ScrapingSource, ScrapingJob,
    UserJobInteraction, SearchHistory,
    JobStatusEnum, ApplicationStatusEnum, ScrapingStatusEnum, UserRoleEnum
)
from ..app.models.job_models import (
    UserCreate, UserUpdate, UserProfile,
    CompanyCreate, CompanyUpdate,
    JobOfferCreate, JobOfferUpdate,
    ScrapingSourceCreate, ScrapingSourceUpdate,
    ScrapingJobCreate,
    UserJobInteractionCreate, SearchHistoryCreate,
    JobSearchFilters, PaginationParams,
    LoginRequest, Token
)


class TestPydanticSchemas:
    """Tests para esquemas Pydantic de validación."""
    
    def test_user_create_valid(self):
        """Test creación de usuario válido."""
        user_data = {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "password": "Password123!",
            "perfil_json": {"skills": ["Python", "FastAPI"]}
        }
        user = UserCreate(**user_data)
        assert user.nombre == "Juan Pérez"
        assert user.email == "juan@example.com"
        assert user.password == "Password123!"
        assert user.perfil_json["skills"] == ["Python", "FastAPI"]
    
    def test_user_create_invalid_email(self):
        """Test validación de email inválido."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                nombre="Juan",
                email="email-invalido",
                password="Password123!"
            )
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_user_create_weak_password(self):
        """Test validación de contraseña débil."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                nombre="Juan",
                email="juan@example.com",
                password="123"  # Muy débil
            )
        assert "La contraseña debe tener al menos una mayúscula" in str(exc_info.value)
    
    def test_user_profile_valid(self):
        """Test perfil de usuario válido."""
        profile = UserProfile(
            habilidades=["Python", "JavaScript"],
            experiencia_anos=5,
            salario_minimo=Decimal("40000"),
            salario_maximo=Decimal("60000"),
            modalidad_trabajo=["remoto", "híbrido"],
            idiomas={"español": "nativo", "inglés": "avanzado"}
        )
        assert len(profile.habilidades) == 2
        assert profile.experiencia_anos == 5
        assert profile.salario_minimo == Decimal("40000")
    
    def test_user_profile_invalid_salary_range(self):
        """Test validación de rango de salario inválido."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                salario_minimo=Decimal("60000"),
                salario_maximo=Decimal("40000")  # Menor que el mínimo
            )
        assert "El salario máximo debe ser mayor al mínimo" in str(exc_info.value)
    
    def test_company_create_valid(self):
        """Test creación de empresa válida."""
        company = CompanyCreate(
            nombre="TechCorp",
            sector="Tecnología",
            sitio_web="https://techcorp.com",
            descripcion="Empresa de desarrollo de software"
        )
        assert company.nombre == "TechCorp"
        assert company.sector == "Tecnología"
        assert str(company.sitio_web) == "https://techcorp.com/"
    
    def test_job_offer_create_valid(self):
        """Test creación de oferta laboral válida."""
        job = JobOfferCreate(
            titulo="Desarrollador Python Senior",
            descripcion="Desarrollo de APIs con FastAPI",
            empresa_id=1,
            ubicacion="Madrid",
            salario=Decimal("55000"),
            url="https://example.com/job/123",
            requisitos=["Python", "FastAPI", "PostgreSQL"],
            modalidad="remoto"
        )
        assert job.titulo == "Desarrollador Python Senior"
        assert job.empresa_id == 1
        assert job.salario == Decimal("55000")
        assert "Python" in job.requisitos
    
    def test_job_offer_create_invalid_title(self):
        """Test validación de título muy corto."""
        with pytest.raises(ValidationError) as exc_info:
            JobOfferCreate(
                titulo="Dev",  # Muy corto
                empresa_id=1,
                url="https://example.com/job/123"
            )
        assert "at least 5 characters" in str(exc_info.value)
    
    def test_scraping_source_create_valid(self):
        """Test creación de fuente de scraping válida."""
        source = ScrapingSourceCreate(
            nombre="LinkedIn",
            base_url="https://linkedin.com/jobs",
            selectors={
                "title": ".job-title",
                "company": ".company-name"
            },
            delay_seconds=2.0,
            max_pages=50
        )
        assert source.nombre == "LinkedIn"
        assert source.delay_seconds == 2.0
        assert source.selectors["title"] == ".job-title"
    
    def test_job_search_filters_valid(self):
        """Test filtros de búsqueda válidos."""
        filters = JobSearchFilters(
            search_query="Python Developer",
            ubicacion=["Madrid", "Barcelona"],
            salario_min=Decimal("40000"),
            salario_max=Decimal("80000"),
            modalidad=["remoto", "híbrido"],
            solo_activas=True
        )
        assert filters.search_query == "Python Developer"
        assert len(filters.ubicacion) == 2
        assert filters.salario_min == Decimal("40000")
    
    def test_pagination_params_valid(self):
        """Test parámetros de paginación válidos."""
        pagination = PaginationParams(
            page=2,
            size=50,
            sort_by="salario",
            sort_order="desc"
        )
        assert pagination.page == 2
        assert pagination.size == 50
        assert pagination.sort_by == "salario"
    
    def test_pagination_params_invalid(self):
        """Test parámetros de paginación inválidos."""
        with pytest.raises(ValidationError):
            PaginationParams(
                page=0,  # Debe ser >= 1
                size=200  # Debe ser <= 100
            )
    
    def test_login_request_valid(self):
        """Test request de login válido."""
        login = LoginRequest(
            email="user@example.com",
            password="Password123!"
        )
        assert login.email == "user@example.com"
        assert login.password == "Password123!"


class TestORMModels:
    """Tests para modelos ORM de SQLAlchemy."""
    
    def test_user_model_creation(self, db):
        """Test creación de usuario en base de datos."""
        user = User(
            nombre="Test User",
            email="test@example.com",
            hashed_password="hashed_password_123",
            role=UserRoleEnum.USER,
            perfil_json={"skills": ["Python"]}
        )
        db.add(user)
        db.commit()
        
        assert user.id is not None
        assert user.nombre == "Test User"
        assert user.email == "test@example.com"
        assert user.role == UserRoleEnum.USER
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_email_unique_constraint(self, db):
        """Test constraint de email único."""
        # Crear primer usuario
        user1 = User(
            nombre="User 1",
            email="same@example.com",
            hashed_password="hash1"
        )
        db.add(user1)
        db.commit()
        
        # Intentar crear segundo usuario con mismo email
        user2 = User(
            nombre="User 2",
            email="same@example.com",
            hashed_password="hash2"
        )
        db.add(user2)
        
        with pytest.raises(IntegrityError):
            db.commit()
    
    def test_company_model_creation(self, db):
        """Test creación de empresa en base de datos."""
        company = Company(
            nombre="Test Company",
            sector="Tecnología",
            sitio_web="https://testcompany.com",
            descripcion="Empresa de prueba"
        )
        db.add(company)
        db.commit()
        
        assert company.id is not None
        assert company.nombre == "Test Company"
        assert company.sector == "Tecnología"
        assert company.created_at is not None
    
    def test_job_offer_model_creation(self, db, test_company):
        """Test creación de oferta laboral en base de datos."""
        job = JobOffer(
            titulo="Test Job",
            descripcion="Job description",
            empresa_id=test_company.id,
            ubicacion="Madrid",
            salario=Decimal("50000"),
            url="https://example.com/job/1",
            status=JobStatusEnum.ACTIVE,
            requisitos=["Python", "FastAPI"],
            modalidad="remoto"
        )
        db.add(job)
        db.commit()
        
        assert job.id is not None
        assert job.titulo == "Test Job"
        assert job.empresa_id == test_company.id
        assert job.status == JobStatusEnum.ACTIVE
        assert job.requisitos == ["Python", "FastAPI"]
        assert job.fecha_scrapeo is not None
    
    def test_job_offer_url_unique_constraint(self, db, test_company):
        """Test constraint de URL única en ofertas."""
        url = "https://example.com/unique-job"
        
        # Crear primera oferta
        job1 = JobOffer(
            titulo="Job 1",
            empresa_id=test_company.id,
            url=url
        )
        db.add(job1)
        db.commit()
        
        # Intentar crear segunda oferta con misma URL
        job2 = JobOffer(
            titulo="Job 2",
            empresa_id=test_company.id,
            url=url
        )
        db.add(job2)
        
        with pytest.raises(IntegrityError):
            db.commit()
    
    def test_company_job_relationship(self, db, test_company):
        """Test relación entre empresa y ofertas laborales."""
        # Crear ofertas para la empresa
        job1 = JobOffer(
            titulo="Job 1",
            empresa_id=test_company.id,
            url="https://example.com/job1"
        )
        job2 = JobOffer(
            titulo="Job 2",
            empresa_id=test_company.id,
            url="https://example.com/job2"
        )
        
        db.add_all([job1, job2])
        db.commit()
        
        # Verificar relación
        db.refresh(test_company)
        assert len(test_company.ofertas) == 2
        assert job1 in test_company.ofertas
        assert job2 in test_company.ofertas
        
        # Verificar relación inversa
        assert job1.empresa == test_company
        assert job2.empresa == test_company
    
    def test_scraping_source_model_creation(self, db):
        """Test creación de fuente de scraping."""
        source = ScrapingSource(
            nombre="Test Source",
            base_url="https://testsource.com",
            selectors={"title": ".title", "company": ".company"},
            delay_seconds=Decimal("1.5"),
            max_pages=20
        )
        db.add(source)
        db.commit()
        
        assert source.id is not None
        assert source.nombre == "Test Source"
        assert source.is_active is True
        assert source.selectors["title"] == ".title"
        assert source.total_jobs_scraped == 0
    
    def test_scraping_job_model_creation(self, db, test_scraping_source, test_user):
        """Test creación de trabajo de scraping."""
        scraping_job = ScrapingJob(
            source_id=test_scraping_source.id,
            user_id=test_user.id,
            search_terms=["Python", "Developer"],
            location_filters=["Madrid"],
            max_results=100,
            status=ScrapingStatusEnum.PENDING
        )
        db.add(scraping_job)
        db.commit()
        
        assert scraping_job.id is not None
        assert scraping_job.source_id == test_scraping_source.id
        assert scraping_job.user_id == test_user.id
        assert scraping_job.status == ScrapingStatusEnum.PENDING
        assert scraping_job.search_terms == ["Python", "Developer"]
    
    def test_user_job_interaction_model(self, db, test_user, test_job_offer):
        """Test modelo de interacción usuario-oferta."""
        interaction = UserJobInteraction(
            user_id=test_user.id,
            job_id=test_job_offer.id,
            action="viewed",
            metadata={"source": "search", "time_spent": 30}
        )
        db.add(interaction)
        db.commit()
        
        assert interaction.id is not None
        assert interaction.user_id == test_user.id
        assert interaction.job_id == test_job_offer.id
        assert interaction.action == "viewed"
        assert interaction.metadata["time_spent"] == 30
    
    def test_search_history_model(self, db, test_user):
        """Test modelo de historial de búsquedas."""
        search = SearchHistory(
            user_id=test_user.id,
            search_query="Python Developer Madrid",
            filters_applied={"location": "Madrid", "salary_min": 40000},
            results_count=25
        )
        db.add(search)
        db.commit()
        
        assert search.id is not None
        assert search.user_id == test_user.id
        assert search.search_query == "Python Developer Madrid"
        assert search.filters_applied["location"] == "Madrid"
        assert search.results_count == 25
    
    def test_user_relationships(self, db, test_user, test_job_offer):
        """Test relaciones del usuario con otras entidades."""
        # Crear interacción
        interaction = UserJobInteraction(
            user_id=test_user.id,
            job_id=test_job_offer.id,
            action="saved"
        )
        
        # Crear búsqueda
        search = SearchHistory(
            user_id=test_user.id,
            search_query="Test search",
            results_count=10
        )
        
        db.add_all([interaction, search])
        db.commit()
        
        # Verificar relaciones
        db.refresh(test_user)
        assert len(test_user.job_interactions) == 1
        assert len(test_user.search_history) == 1
        assert test_user.job_interactions[0].action == "saved"
        assert test_user.search_history[0].search_query == "Test search"


class TestEnums:
    """Tests para enums del sistema."""
    
    def test_job_status_enum(self):
        """Test enum de estados de trabajo."""
        assert JobStatusEnum.ACTIVE.value == "active"
        assert JobStatusEnum.EXPIRED.value == "expired"
        assert JobStatusEnum.FILLED.value == "filled"
        assert JobStatusEnum.DRAFT.value == "draft"
    
    def test_application_status_enum(self):
        """Test enum de estados de aplicación."""
        assert ApplicationStatusEnum.PENDING.value == "pending"
        assert ApplicationStatusEnum.APPLIED.value == "applied"
        assert ApplicationStatusEnum.INTERVIEWING.value == "interviewing"
        assert ApplicationStatusEnum.REJECTED.value == "rejected"
        assert ApplicationStatusEnum.ACCEPTED.value == "accepted"
    
    def test_scraping_status_enum(self):
        """Test enum de estados de scraping."""
        assert ScrapingStatusEnum.PENDING.value == "pending"
        assert ScrapingStatusEnum.RUNNING.value == "running"
        assert ScrapingStatusEnum.COMPLETED.value == "completed"
        assert ScrapingStatusEnum.FAILED.value == "failed"
        assert ScrapingStatusEnum.PAUSED.value == "paused"
    
    def test_user_role_enum(self):
        """Test enum de roles de usuario."""
        assert UserRoleEnum.USER.value == "user"
        assert UserRoleEnum.ADMIN.value == "admin"
        assert UserRoleEnum.SCRAPER.value == "scraper"


class TestModelValidations:
    """Tests para validaciones específicas de modelos."""
    
    def test_job_offer_title_validation(self):
        """Test validación de título de oferta."""
        # Título válido
        job = JobOfferCreate(
            titulo="Desarrollador Python Senior",
            empresa_id=1,
            url="https://example.com/job"
        )
        assert job.titulo == "Desarrollador Python Senior"
        
        # Título se convierte a title case
        job2 = JobOfferCreate(
            titulo="desarrollador python senior",
            empresa_id=1,
            url="https://example.com/job2"
        )
        assert job2.titulo == "Desarrollador Python Senior"
    
    def test_scraping_source_delay_validation(self):
        """Test validación de delay en fuente de scraping."""
        # Delay válido
        source = ScrapingSourceCreate(
            nombre="Test",
            base_url="https://test.com",
            delay_seconds=1.5
        )
        assert source.delay_seconds == 1.5
        
        # Delay muy bajo
        with pytest.raises(ValidationError):
            ScrapingSourceCreate(
                nombre="Test",
                base_url="https://test.com",
                delay_seconds=0.05  # Menor que 0.1
            )
        
        # Delay muy alto
        with pytest.raises(ValidationError):
            ScrapingSourceCreate(
                nombre="Test",
                base_url="https://test.com",
                delay_seconds=15.0  # Mayor que 10.0
            )
    
    def test_pagination_validation(self):
        """Test validación de parámetros de paginación."""
        # Parámetros válidos
        pagination = PaginationParams(page=1, size=20)
        assert pagination.page == 1
        assert pagination.size == 20
        
        # Página inválida
        with pytest.raises(ValidationError):
            PaginationParams(page=0, size=20)
        
        # Tamaño inválido
        with pytest.raises(ValidationError):
            PaginationParams(page=1, size=200)
        
        # Sort by inválido
        with pytest.raises(ValidationError):
            PaginationParams(page=1, size=20, sort_by="invalid_field")


class TestModelMethods:
    """Tests para métodos de modelos."""
    
    def test_user_repr(self, test_user):
        """Test representación string de usuario."""
        repr_str = repr(test_user)
        assert "User" in repr_str
        assert str(test_user.id) in repr_str
        assert test_user.nombre in repr_str
        assert test_user.email in repr_str
    
    def test_company_repr(self, test_company):
        """Test representación string de empresa."""
        repr_str = repr(test_company)
        assert "Company" in repr_str
        assert str(test_company.id) in repr_str
        assert test_company.nombre in repr_str
    
    def test_job_offer_repr(self, test_job_offer):
        """Test representación string de oferta laboral."""
        repr_str = repr(test_job_offer)
        assert "JobOffer" in repr_str
        assert str(test_job_offer.id) in repr_str
        assert test_job_offer.titulo in repr_str
        assert str(test_job_offer.empresa_id) in repr_str