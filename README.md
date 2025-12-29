# Job Seeker Assistant

## Resumen del Proyecto

Job Seeker Assistant es una herramienta diseñada para simplificar y organizar la búsqueda de empleo. Consta de un backend en Django y una extensión de navegador que trabajan juntos para permitir a los usuarios guardar, gestionar y seguir el estado de sus postulaciones a ofertas de trabajo directamente desde el navegador.

## Características Principales

- **Backend con Django REST Framework:** Una API robusta para gestionar ofertas de trabajo, postulaciones y usuarios.
- **Extensión de Navegador:** Permite a los usuarios capturar información de ofertas de trabajo desde cualquier sitio web con un solo clic.
- **Base de Datos SQLite:** Almacenamiento ligero y sencillo para un desarrollo rápido.
- **Gestión de Entorno con Nix:** Entorno de desarrollo reproducible y consistente.

## Cómo Poner en Marcha el Proyecto

A continuación, se detallan los pasos para configurar y ejecutar tanto el backend como el frontend.

### Prerrequisitos

- [Nix](https://nixos.org/download.html) instalado en tu sistema.
- Un navegador compatible con extensiones (ej. Google Chrome, Firefox).

### Configuración del Backend (Django)

1.  **Activar el Entorno Virtual:**
    El entorno de Nix gestiona automáticamente la instalación de Python y las dependencias. Para activar el entorno virtual y poder usar los comandos de Django, ejecuta:
    ```bash
    source .venv/bin/activate
    ```

2.  **Aplicar las Migraciones:**
    Para crear las tablas en la base de datos, ejecuta:
    ```bash
    python backend/manage.py migrate
    ```

3.  **Iniciar el Servidor de Desarrollo:**
    Utiliza el script proporcionado para iniciar el servidor de Django. Este se ejecutará en `http://127.0.0.1:8000`.
    ```bash
    ./devserver.sh
    ```

### Configuración del Frontend (Extensión de Navegador)

1.  **Cargar la Extensión en el Navegador:**
    - Abre tu navegador (ej. Chrome) y ve a la página de gestión de extensiones (`chrome://extensions`).
    - Activa el "Modo de desarrollador".
    - Haz clic en "Cargar descomprimida" y selecciona la carpeta `frontend/` de este proyecto.

2.  **Configurar el ID de la Extensión (Opcional, para desarrollo avanzado):
    - Una vez cargada, la extensión tendrá un ID único. Si necesitas interactuar con ella desde otros scripts o configuraciones, puedes encontrar este ID en la página de detalles de la extensión.

## Próximos Pasos

- **Desarrollar la Interfaz de la Extensión:** Crear el formulario y la lógica en el popup de la extensión para capturar los datos y enviarlos a la API del backend.
- **Implementar Autenticación de Usuarios:** Añadir un sistema de registro e inicio de sesión para que cada usuario gestione sus propias postulaciones.
- **Mejorar la API:** Añadir endpoints para listar, actualizar y eliminar ofertas y postulaciones.
- **Refinar la Configuración de CORS:** Ajustar la configuración de CORS en `settings.py` para producción, especificando los orígenes permitidos en lugar de `CORS_ALLOW_ALL_ORIGINS=True`.

