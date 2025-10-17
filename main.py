# main.py
import uvicorn
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from prometheus_client import make_asgi_app
from typing import Dict, Any
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

# Módulos internos
from fastapi.security import OAuth2PasswordRequestForm # ¡Nuevo!
import asyncio

from security import ( # Asegúrate de importar estas variables y funciones
    get_current_user,
    get_authorized_user,
    Role,
    FAKE_USERS_DB, # Importar la base de datos simulada
    create_access_token # Importar la función para crear el token
)
from security import get_current_user, get_authorized_user, Role
from sensors import SensorData, SENSOR_REGISTRY
from processing import process_sensor_data_concurrently
from websocket import ConnectionManager
from metrics import request_counter, processing_latency

# --- Configuración Inicial ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(
    title="Stark Industries Concurrent Security System",
    description="Sistema de seguridad concurrente con FastAPI y asyncio [cite: 1, 5]",
    version="1.0.0"
)

manager = ConnectionManager()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Montar las métricas de Prometheus en /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# --- Rutas de Gestión de Sensores ---

# main.py (FRAGMENTO CORREGIDO PARA EVITAR EL ERROR 500)

# main.py (Opción B: PARA LANZAR EN SEGUNDO PLANO Y DEVOLVER INMEDIATAMENTE)

# main.py

@app.post("/sensor/event", status_code=status.HTTP_202_ACCEPTED)
# @request_counter.track_inprogress()  # <-- Comentado para la prueba
# @processing_latency.time()         # <-- Comentado para la prueba
async def receive_sensor_event(data: SensorData):
    """
    Recibe un evento de sensor y lo procesa de forma concurrente.
    """
    logging.info(f"Evento recibido de {data.sensor_type}: {data.value}")

    if data.sensor_type not in SENSOR_REGISTRY:
        logging.warning(f"Tipo de sensor desconocido: {data.sensor_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sensor '{data.sensor_type}' no registrado."
        )

    # Ahora puedes descomentar esta línea si quieres, aunque el resultado será el mismo
    asyncio.create_task(process_sensor_data_concurrently(data, manager))

    return {"message": "Prueba final sin decoradores personalizados", "sensor": data.sensor_type}
@app.get("/system/status")
async def get_system_status(
    # La llamada a get_authorized_user() devuelve la función 'role_verifier',
    # y la envolvemos en un solo Depends().
    current_user: Dict[str, Any] = Depends(get_authorized_user([Role.ADMIN, Role.OPERATOR, Role.VIEWER]))
):
    """Acceso de solo lectura al estado del sistema."""
    return {"status": "ONLINE", "user": current_user["username"], "role": current_user["role"]}

@app.post("/system/reset")
async def system_reset(
    current_user: Dict[str, Any] = Depends(get_authorized_user([Role.ADMIN]))
):
    """Ruta protegida: solo Administradores pueden resetear."""
    logging.warning(f"¡Reinicio del sistema iniciado por el Admin: {current_user['username']}!")
    # Aquí iría la lógica real de reinicio
    return {"message": "Sistema de seguridad reiniciado", "by_admin": current_user["username"]}

# ...
@app.get("/")
async def get_index():
    """Sirve el archivo index.html."""
    from fastapi.responses import FileResponse
    # Devuelve directamente el archivo estático
    return FileResponse("static/index.html")


# main.py (Añadir la ruta /token)

# ... (Configuración de FastAPI y app.mounts) ...

# --- Rutas de Autenticación (para que el HTML pueda iniciar sesión) ---

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para que el cliente obtenga un token JWT.
    """
    user = FAKE_USERS_DB.get(form_data.username)

    # En un sistema real, aquí verificarías el hash de la contraseña:
    # if not verify_password(form_data.password, user["hashed_password"]):

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}


# ... (El resto de tus rutas POST /sensor/event, GET /system/status, etc., se quedan igual) ...

# --- Ruta de WebSocket ---
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint para que los clientes se conecten y reciban alertas en tiempo real.
    """
    await manager.connect(websocket)
    try:
        # El loop del WebSocket espera mensajes del cliente, aunque nuestro caso es mostly server-to-client
        while True:
            # Aquí podríamos recibir mensajes del cliente, pero para este sistema lo ignoramos.
            # Simplemente mantenemos la conexión abierta.
            data = await websocket.receive_text()
            # Opcional: registrar que el cliente está vivo (heartbeat)
            # logging.info(f"Mensaje del cliente: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info("Cliente WebSocket desconectado.")
# La conexión WebSocket se gestiona en el manager
# Se omite el código del endpoint de WebSocket aquí por brevedad, pero usaría el ConnectionManager
# como se describe en el punto 5 de la solución[cite: 50, 51].

# Para correr: uvicorn main:app --reload