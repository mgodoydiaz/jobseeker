# __init__.py
# Archivo de inicialización del paquete tests
# Configuración base para pruebas unitarias
# IMPLEMENTADO: Configuración base para pytest con fixtures compartidas

import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from ..app.database.connection import Base, get_db
from ..app.main import app
from ..app.core.config import settings


# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Override de la función get_db para usar base de datos de prueba.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override de la dependencia de base de datos
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture para manejar el event loop de asyncio en las pruebas.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> Generator:
    """
    Fixture que proporciona un cliente de prueba para FastAPI.
    """
    # Crear las tablas de prueba
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
    
    # Limpiar después de las pruebas
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Fixture que proporciona una sesión de base de datos para cada prueba.
    """
    # Crear las tablas para cada prueba
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpiar después de cada prueba
        Base.metadata.drop_all(bind=engine)