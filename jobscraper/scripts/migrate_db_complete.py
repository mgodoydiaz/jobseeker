# migrate_db.py
# Script para migraciones de base de datos
# Utilidad para crear, actualizar y gestionar el esquema de la BD

import sys
import os
from pathlib import Path

# Agregar el directorio raiz al path para importar modulos
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from jobscraper.app.database.connection import Base, engine, DATABASE_URL
from jobscraper.app.models.database_models import *  # Importar todos los modelos
from jobscraper.config import settings


def create_database_if_not_exists():
    """
    Crear la base de datos si no existe.
    Util para configuracion inicial.
    """
    try:
        # Extraer informacion de la URL de conexion
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        db_name = parsed.path[1:]  # Remover el '/' inicial
        host = parsed.hostname
        port = parsed.port or 5432
        user = parsed.username
        password = parsed.password
        
        # Conectar a PostgreSQL sin especificar base de datos
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Base de datos por defecto
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creando base de datos '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Base de datos '{db_name}' creada exitosamente")
        else:
            print(f"Base de datos '{db_name}' ya existe")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
        return False
    
    return True


def create_tables():
    """
    Crear todas las tablas definidas en los modelos.
    """
    try:
        print("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente")
        return True
    except Exception as e:
        print(f"Error al crear tablas: {e}")
        return False


def drop_tables():
    """
    Eliminar todas las tablas.
    USAR CON PRECAUCION - ELIMINA TODOS LOS DATOS
    """
    try:
        print("Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        print("Tablas eliminadas exitosamente")
        return True
    except Exception as e:
        print(f"Error al eliminar tablas: {e}")
        return False


def check_database_connection():
    """
    Verificar la conexion a la base de datos.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Conexion a la base de datos exitosa")
            return True
    except Exception as e:
        print(f"Error de conexion a la base de datos: {e}")
        return False


def show_tables():
    """
    Mostrar todas las tablas existentes en la base de datos.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            if tables:
                print("\nTablas existentes en la base de datos:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("No hay tablas en la base de datos")
                
            return True
    except Exception as e:
        print(f"Error al consultar tablas: {e}")
        return False


def insert_sample_data():
    """
    Insertar datos de ejemplo para testing.
    """
    try:
        from jobscraper.app.database.connection import SessionLocal
        from jobscraper.app.database.crud import create_company, create_scraping_source
        from jobscraper.app.models.job_models import CompanyCreate, ScrapingSourceCreate
        
        db = SessionLocal()
        
        print("Insertando datos de ejemplo...")
        
        # Crear empresas de ejemplo
        companies_data = [
            {
                "nombre": "TechCorp",
                "sector": "Tecnologia",
                "sitio_web": "https://techcorp.com",
                "descripcion": "Empresa lider en desarrollo de software",
                "tamano": "grande",
                "ubicacion": "Madrid, España"
            },
            {
                "nombre": "StartupInnovate",
                "sector": "Fintech",
                "sitio_web": "https://startupinnovate.com",
                "descripcion": "Startup innovadora en servicios financieros",
                "tamano": "startup",
                "ubicacion": "Barcelona, España"
            }
        ]
        
        for company_data in companies_data:
            company = CompanyCreate(**company_data)
            create_company(db, company)
        
        # Crear fuentes de scraping de ejemplo
        sources_data = [
            {
                "nombre": "InfoJobs",
                "base_url": "https://www.infojobs.net",
                "descripcion": "Portal de empleo lider en España",
                "selectors": {
                    "job_title": ".job-title",
                    "company": ".company-name",
                    "location": ".location",
                    "description": ".description"
                },
                "headers": {
                    "User-Agent": "JobScraper-Bot/1.0"
                },
                "delay_seconds": 2.0,
                "max_pages": 5
            },
            {
                "nombre": "LinkedIn Jobs",
                "base_url": "https://www.linkedin.com/jobs",
                "descripcion": "Red profesional con ofertas de empleo",
                "selectors": {
                    "job_title": ".job-title-link",
                    "company": ".company-name-link",
                    "location": ".job-location",
                    "description": ".job-description"
                },
                "headers": {
                    "User-Agent": "JobScraper-Bot/1.0"
                },
                "delay_seconds": 3.0,
                "max_pages": 3
            }
        ]
        
        for source_data in sources_data:
            source = ScrapingSourceCreate(**source_data)
            create_scraping_source(db, source)
        
        db.close()
        print("Datos de ejemplo insertados exitosamente")
        return True
        
    except Exception as e:
        print(f"Error al insertar datos de ejemplo: {e}")
        return False


def main():
    """
    Funcion principal del script de migracion.
    """
    print("JobScraper - Script de Migracion de Base de Datos")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("""
Uso: python migrate_db.py <comando>

Comandos disponibles:
  init        - Inicializar base de datos (crear DB + tablas + datos ejemplo)
  create-db   - Crear base de datos si no existe
  create      - Crear todas las tablas
  drop        - Eliminar todas las tablas (PELIGROSO)
  check       - Verificar conexion a la base de datos
  tables      - Mostrar tablas existentes
  sample-data - Insertar datos de ejemplo
  reset       - Eliminar y recrear todo (PELIGROSO)
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        print("Inicializando base de datos completa...")
        if (create_database_if_not_exists() and 
            check_database_connection() and 
            create_tables() and 
            insert_sample_data()):
            print("\nInicializacion completada exitosamente")
        else:
            print("\nError durante la inicializacion")
    
    elif command == "create-db":
        create_database_if_not_exists()
    
    elif command == "create":
        if check_database_connection():
            create_tables()
    
    elif command == "drop":
        response = input("Estas seguro de que quieres eliminar todas las tablas? (si/no): ")
        if response.lower() in ['si', 'yes', 'y']:
            if check_database_connection():
                drop_tables()
        else:
            print("Operacion cancelada")
    
    elif command == "check":
        check_database_connection()
    
    elif command == "tables":
        if check_database_connection():
            show_tables()
    
    elif command == "sample-data":
        if check_database_connection():
            insert_sample_data()
    
    elif command == "reset":
        response = input("Estas seguro de que quieres resetear toda la base de datos? (si/no): ")
        if response.lower() in ['si', 'yes', 'y']:
            if (check_database_connection() and 
                drop_tables() and 
                create_tables() and 
                insert_sample_data()):
                print("\nReset completado exitosamente")
            else:
                print("\nError durante el reset")
        else:
            print("Operacion cancelada")
    
    else:
        print(f"Comando desconocido: {command}")


if __name__ == "__main__":
    main()