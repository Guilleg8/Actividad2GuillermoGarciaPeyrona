import uvicorn
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from prometheus_client import make_asgi_app
from typing import Dict, Any, Set, Optional
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

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
from sensors import SensorData, SENSOR_REGISTRY, Alert
from processing import process_sensor_data_concurrently, send_push_notification_async, send_email_async
from websocket import ConnectionManager
from metrics import request_counter, processing_latency
from metrics import events_processed

background_tasks: Set[asyncio.Task] = set()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(
    title="Stark Industries Concurrent Security System",
    description="Sistema de seguridad concurrente con FastAPI y asyncio [cite: 1, 5]",
    version="1.0.0"
)

manager = ConnectionManager()

background_tasks: Set[asyncio.Task] = set()
app.mount("/static", StaticFiles(directory="static"), name="static")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.post("/sensor/event", status_code=status.HTTP_202_ACCEPTED)
async def receive_sensor_event(data: SensorData, alert=None):
    logging.info(f"Evento recibido de {data.sensor_type}: {data.value}")

    if data.sensor_type not in SENSOR_REGISTRY:
        logging.warning(f"Tipo de sensor desconocido: {data.sensor_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sensor '{data.sensor_type}' no registrado."
        )
    email_task = asyncio.create_task(send_email_async(alert))
    push_task = asyncio.create_task(send_push_notification_async(alert))

    background_tasks.add(email_task)
    background_tasks.add(push_task)

    email_task.add_done_callback(background_tasks.discard)
    push_task.add_done_callback(background_tasks.discard)

    return {"message": "Prueba final sin decoradores personalizados", "sensor": data.sensor_type}

@app.get("/system/status")
async def get_system_status(
    current_user: Dict[str, Any] = Depends(get_authorized_user([Role.ADMIN, Role.OPERATOR, Role.VIEWER]))
):
    return {"status": "ONLINE", "user": current_user["username"], "role": current_user["role"]}

@app.post("/system/reset")
async def system_reset(
    current_user: Dict[str, Any] = Depends(get_authorized_user([Role.ADMIN]))
):
    logging.warning(f"¡Reinicio del sistema iniciado por el Admin: {current_user['username']}!")
    return {"message": "Sistema de seguridad reiniciado", "by_admin": current_user["username"]}

@app.get("/")
async def get_index():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    user = FAKE_USERS_DB.get(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info("Cliente WebSocket desconectado.")
