🛡️ Stark Industries - Sistema de Seguridad ConcurrenteEste proyecto es un sistema de seguridad simulado inspirado en Stark Industries, desarrollado con FastAPI. La aplicación está diseñada para procesar eventos de múltiples sensores de forma concurrente, gestionar la autenticación de usuarios con diferentes roles y notificar alertas en tiempo real a través de WebSockets.✨ Características PrincipalesProcesamiento Concurrente: Utiliza asyncio y ThreadPoolExecutor para manejar eventos de sensores de manera asíncrona y no bloqueante, asegurando que el sistema pueda escalar y responder rápidamente.Alertas en Tiempo Real: Implementa un sistema de notificaciones en tiempo real con WebSockets, que difunde las alertas a todos los clientes conectados al dashboard.Autenticación y Autorización: Sistema de seguridad basado en tokens JWT (OAuth2) con un control de acceso basado en roles (RBAC) para proteger las rutas de la API.Dashboard Interactivo: Una interfaz de usuario web simple creada con HTML y JavaScript para iniciar sesión, simular eventos de sensores y visualizar alertas en tiempo real.Monitorización: Integración con Prometheus para exportar métricas clave de la aplicación, como la latencia de procesamiento y el número de eventos gestionados.Arquitectura Modular: El código está organizado en módulos lógicos para una mejor mantenibilidad (security.py, sensors.py, processing.py, etc.).🚀 Tecnologías UtilizadasBackend: Python 3, FastAPI, UvicornSeguridad: python-jose, passlib, OAuth2Concurrencia: asyncio, concurrent.futuresMonitorización: prometheus-clientFrontend: HTML, JavaScript (sin frameworks)🔧 Instalación y ConfiguraciónClonar el repositorio:Bashgit clone <URL-DE-TU-REPOSITORIO>
cd <nombre-del-repositorio>
Crear y activar un entorno virtual:Bashpython -m venv .venv
# En Windows
.venv\Scripts\activate
# En macOS/Linux
source .venv/bin/activate
Instalar las dependencias:Crea un archivo requirements.txt con el siguiente contenido y luego ejecútalo.requirements.txt:fastapi
uvicorn[standard]
pydantic
python-jose[cryptography]
passlib[bcrypt]
prometheus-client
Jinja2
python-multipart
Comando de instalación:Bashpip install -r requirements.txt
▶️ Cómo Ejecutar el ProyectoUna vez instaladas las dependencias, inicia el servidor de desarrollo Uvicorn desde la raíz del proyecto:Bashuvicorn main:app --reload
El servidor estará disponible en http://127.0.0.1:8000.⚙️ Cómo Usar la AplicaciónAbre el Dashboard: Navega a http://127.0.0.1:8000 en tu navegador.Inicia Sesión: Utiliza una de las credenciales de prueba para obtener un token de acceso.Simula Eventos: Usa el formulario de sensores para enviar eventos. Por ejemplo, selecciona el sensor de motion y envía el valor MOVIMIENTO_NO_AUTORIZADO para generar una alerta crítica.Visualiza Alertas: Las alertas generadas aparecerán en tiempo real en la sección "Alertas en Tiempo Real".Prueba Rutas Protegidas: (Si has dejado visibles los botones) Intenta acceder a las rutas de sistema para verificar el control de acceso por roles.Credenciales de PruebaUsuarioContraseñaRoltonyironmanAdminrhodeywar-machineOperatorpepperrescueViewer📝 Estructura del Proyecto.
├── main.py              # Aplicación principal FastAPI y definición de rutas.
├── processing.py        # Lógica para el procesamiento concurrente de datos.
├── security.py          # Módulo de autenticación (JWT) y autorización (roles).
├── sensors.py           # Definición de las clases de sensores.
├── websocket.py         # Gestor de conexiones WebSocket.
├── metrics.py           # Configuración de las métricas de Prometheus.
└── static/
    ├── index.html       # Interfaz de usuario del dashboard.
    └── script.js        # Lógica del frontend (conexión WebSocket, peticiones API).
