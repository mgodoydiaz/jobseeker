# Job Seeker Assistant

## Resumen del Proyecto

Job Seeker Assistant es una herramienta diseñada para simplificar y organizar la búsqueda de empleo. Consta de un backend en Django y una aplicación web en React que también funciona como extensión de navegador. Permite a los usuarios guardar, gestionar y analizar ofertas de trabajo directamente desde la web.

## Características Principales

- **Backend con Django REST Framework:** Una API robusta para analizar y gestionar ofertas de trabajo.
- **Frontend con React y Vite:** Una aplicación web moderna y rápida que sirve como página de inicio y como interfaz para la extensión.
- **Doble Funcionalidad:** Funciona como una página web independiente con una interfaz inspirada en Google y como una potente extensión de Chrome.
- **Modo Oscuro:** La interfaz web cuenta con un selector de tema para una mejor experiencia de usuario.
- **Base de Datos SQLite:** Almacenamiento ligero y sencillo para un desarrollo rápido.
- **Gestión de Entorno con Nix:** Entorno de desarrollo reproducible y consistente.

## Cómo Poner en Marcha el Proyecto

A continuación, se detallan los pasos para configurar y ejecutar tanto el backend como el frontend.

### 1. Backend (Servidor Django)

El backend se encarga de procesar y almacenar los datos de las ofertas de trabajo.

1.  **Activar el Entorno Virtual:**
    Todos los comandos de Python deben ejecutarse dentro del entorno virtual de Nix. Para activarlo, ejecuta:
    ```bash
    source .venv/bin/activate
    ```

2.  **Aplicar las Migraciones:**
    Esto preparará la base de datos para almacenar los datos.
    ```bash
    python mysite/manage.py migrate
    ```

3.  **Iniciar el Servidor de Desarrollo:**
    El proyecto está configurado para usar la tarea de vista previa del IDE. Simplemente ve a la pestaña "Vistas previas" y ejecuta la tarea `web`.

    Si prefieres hacerlo manualmente, ejecuta:
    ```bash
    ./devserver.sh
    ```
    El servidor estará disponible en `http://127.0.0.1:8000`.

### 2. Frontend (Web y Extensión en React)

El frontend es una aplicación React construida con Vite.

1.  **Navegar a la Carpeta del Frontend:**
    ```bash
    cd frontend
    ```

2.  **Instalar Dependencias:**
    Si es la primera vez que configuras el proyecto, necesitas instalar los paquetes de Node.js.
    ```bash
    npm install
    ```

3.  **Ejecutar el Entorno de Desarrollo (Opcional):**
    Si quieres hacer cambios en el frontend y verlos al instante, puedes usar el servidor de desarrollo de Vite. La página web estará disponible en `http://localhost:5173`.
    ```bash
    npm run dev
    ```

4.  **Construir la Aplicación para Producción:**
    Este paso es **esencial** para generar la carpeta `dist/` que se usará para la extensión de Chrome.
    ```bash
    npm run build
    ```

### 3. Cargar la Extensión en Chrome

Una vez que hayas construido el frontend, puedes cargarlo como una extensión en tu navegador.

1.  **Abre Chrome** y ve a la página de gestión de extensiones: `chrome://extensions`.
2.  **Activa el "Modo de desarrollador"** en la esquina superior derecha.
3.  Haz clic en el botón **"Cargar descomprimida"**.
4.  Selecciona la carpeta `frontend/dist/` que se generó en el paso anterior.
5.  ¡Listo! El icono de la extensión aparecerá en tu barra de herramientas.

## Próximos Pasos

- [x] ~~Desarrollar la Interfaz de la Extensión.~~ ¡Hecho!
- [x] ~~Crear una página de inicio para la versión web.~~ ¡Hecho!
- **Implementar la lógica de análisis en la Homepage:** Conectar la barra de búsqueda de la página de inicio para que también pueda analizar URLs.
- **Implementar Autenticación de Usuarios:** Añadir un sistema de registro e inicio de sesión para que cada usuario gestione sus propias postulaciones.
- **Mejorar la API:** Añadir endpoints para listar, actualizar y eliminar ofertas y postulaciones.
- **Refinar la Configuración de CORS:** Ajustar la configuración de CORS en `settings.py` para producción, especificando los orígenes permitidos.