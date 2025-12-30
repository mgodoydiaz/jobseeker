# utils.py
# Funciones utilitarias generales
# Helpers y funciones de apoyo para toda la aplicación
# IMPLEMENTADO: Utilidades para autenticación, hashing y validaciones

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Union, Any
import secrets
import string
import re

from .config import settings


# ==================== CONFIGURACIÓN DE HASHING ====================

# Configurar contexto de hashing para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== FUNCIONES DE CONTRASEÑAS ====================

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """
    Genera una contraseña aleatoria segura.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


# ==================== FUNCIONES JWT ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea un token JWT de refresh.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un token JWT.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# ==================== FUNCIONES DE VALIDACIÓN ====================

def validate_email(email: str) -> bool:
    """
    Valida formato de email usando regex.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Valida la fortaleza de una contraseña.
    Retorna (es_válida, lista_de_errores).
    """
    errors = []
    
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    if not re.search(r'[A-Z]', password):
        errors.append("La contraseña debe tener al menos una mayúscula")
    
    if not re.search(r'[a-z]', password):
        errors.append("La contraseña debe tener al menos una minúscula")
    
    if not re.search(r'\d', password):
        errors.append("La contraseña debe tener al menos un número")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("La contraseña debe tener al menos un carácter especial")
    
    return len(errors) == 0, errors


def validate_url(url: str) -> bool:
    """
    Valida formato de URL usando regex.
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return re.match(pattern, url) is not None


# ==================== FUNCIONES DE FORMATEO ====================

def format_salary(salary: Union[int, float]) -> str:
    """
    Formatea un salario para mostrar.
    """
    if salary >= 1000000:
        return f"€{salary/1000000:.1f}M"
    elif salary >= 1000:
        return f"€{salary/1000:.0f}K"
    else:
        return f"€{salary:.0f}"


def clean_text(text: str) -> str:
    """
    Limpia texto removiendo caracteres especiales y espacios extra.
    """
    if not text:
        return ""
    
    # Remover caracteres especiales excepto básicos
    cleaned = re.sub(r'[^\w\s\-.,!?()áéíóúñüÁÉÍÓÚÑÜ]', '', text)
    
    # Remover espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto a una longitud máxima.
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


# ==================== FUNCIONES DE CONVERSIÓN ====================

def snake_to_camel(snake_str: str) -> str:
    """
    Convierte snake_case a camelCase.
    """
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convierte camelCase a snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


# ==================== FUNCIONES DE TIEMPO ====================

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea datetime a string.
    """
    return dt.strftime(format_str)


def time_ago(dt: datetime) -> str:
    """
    Retorna tiempo transcurrido en formato legible.
    """
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "hace unos segundos"


# ==================== FUNCIONES DE PAGINACIÓN ====================

def calculate_pagination(page: int, size: int, total: int) -> dict:
    """
    Calcula información de paginación.
    """
    total_pages = (total + size - 1) // size
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "page": page,
        "size": size,
        "total": total,
        "pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None
    }


# ==================== FUNCIONES DE LOGGING ====================

def log_user_action(user_id: int, action: str, details: dict = None) -> None:
    """
    Registra una acción del usuario para auditoría.
    """
    import logging
    logger = logging.getLogger("user_actions")
    
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    logger.info(f"User action: {log_data}")


# ==================== FUNCIONES DE SCRAPING ====================

def clean_scraped_text(text: str) -> str:
    """
    Limpia texto scrapeado removiendo HTML y caracteres especiales.
    """
    if not text:
        return ""
    
    # Remover tags HTML básicos
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remover entidades HTML
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # Limpiar espacios
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_salary_from_text(text: str) -> Optional[float]:
    """
    Extrae información de salario de un texto.
    """
    if not text:
        return None
    
    # Patrones para detectar salarios
    patterns = [
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€',  # 50.000€ o 50.000,00€
        r'€\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # €50.000
        r'(\d{1,3}(?:,\d{3})*)\s*k\s*€',          # 50k€
        r'(\d{1,3}(?:\.\d{3})*)\s*euros?',        # 50000 euros
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            salary_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                salary = float(salary_str)
                # Si es en formato k (miles)
                if 'k' in text.lower():
                    salary *= 1000
                return salary
            except ValueError:
                continue
    
    return None