import openai
import os
import json
import time

# --- Configuración de la API de OpenAI ---
# Idealmente, la clave de API debería cargarse de forma segura desde las variables de entorno.
# Para producción, NUNCA la hardcodees en el código.
# openai.api_key = os.getenv("OPENAI_API_KEY", "TU_CLAVE_DE_API_AQUÍ")

# --- Simulación sin una clave de API real ---
# Para evitar errores si no tienes una clave configurada, vamos a simular la respuesta.

def analyze_job_match(user_experience: str, job_description: str) -> dict:
    """
    Simula una llamada a una API de LLM para analizar la adecuación de un perfil a una oferta.

    Args:
        user_experience: Un resumen de la experiencia del usuario.
        job_description: La descripción de la oferta de trabajo.

    Returns:
        Un diccionario con un resumen, una puntuación de compatibilidad y las habilidades que faltan.
    """
    print(f"--- Iniciando análisis simulado de LLM ---")
    print(f"Experiencia del usuario: {user_experience[:100]}...")
    print(f"Descripción de la oferta: {job_description[:100]}...")

    # Simulación de la llamada a la API y el tiempo de espera
    time.sleep(3) # Simula la latencia de la red

    # Respuesta JSON simulada que se esperaría de un LLM
    # En una implementación real, construirías un prompt y harías una llamada como:
    # response = openai.Completion.create(...) o openai.ChatCompletion.create(...)
    simulated_response = {
        "summary": "El perfil del candidato es prometedor, con una sólida experiencia en desarrollo de software, pero carece de experiencia directa en algunas de las tecnologías clave requeridas.",
        "match_score": 75, # Puntuación de 0 a 100
        "missing_skills": [
            "Experiencia específica con Kubernetes",
            "Conocimiento avanzado de GraphQL",
            "Certificación en AWS o Azure"
        ]
    }

    # La respuesta real de la API podría necesitar ser parseada desde una cadena JSON
    # simulated_json_string = json.dumps(simulated_response)
    # analysis = json.loads(simulated_json_string)
    analysis = simulated_response

    # Convertimos la lista de habilidades que faltan a una cadena de texto para guardarla en la BD
    analysis['missing_skills'] = ", ".join(analysis.get('missing_skills', []))

    print(f"--- Análisis simulado completado ---")
    return analysis


# Ejemplo de uso (esto no se ejecutará cuando se importe como módulo)
if __name__ == '__main__':
    # Experiencia de ejemplo de un usuario
    sample_user_experience = """
    Desarrollador de software con más de 5 años de experiencia en Python y Django.
    He trabajado en el desarrollo de APIs RESTful, la optimización de bases de datos con PostgreSQL
    y el despliegue de aplicaciones en Heroku. Apasionado por el código limpio y las buenas prácticas.
    """

    # Descripción de ejemplo de una oferta de trabajo
    sample_job_description = """
    Buscamos un Ingeniero de Backend Senior para unirse a nuestro equipo. Se requiere experiencia
    en Python, Django REST Framework, PostgreSQL y Docker. El candidato ideal tendrá experiencia
    con Kubernetes, GraphQL y plataformas en la nube como AWS o Azure. 
    Responsabilidades: diseñar, construir y mantener APIs eficientes y escalables.
    """

    # Ejecutar el análisis
    match_analysis = analyze_job_match(sample_user_experience, sample_job_description)

    # Imprimir los resultados
    print("\n--- Resultados del Análisis ---")
    print(f"Resumen: {match_analysis['summary']}")
    print(f"Puntuación de Compatibilidad: {match_analysis['match_score']}%")
    print(f"Habilidades que Faltan: {match_analysis['missing_skills']}")

