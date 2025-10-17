# processing.py
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from sensors import SensorData, SENSOR_REGISTRY, Alert
from websocket import ConnectionManager
from metrics import events_processed


# Simulaciones de notificaciones asíncronas [cite: 52]
async def send_email_async(alert: Alert):
    """Simula el envío de correo electrónico asíncrono[cite: 53]."""
    await asyncio.sleep(0.05)  # Simular IO blocking
    logging.info(f"EMAIL Enviado: Alerta {alert.level} de {alert.sensor_id}.")


async def send_push_notification_async(alert: Alert):
    """Simula el envío de notificación push asíncrona[cite: 54]."""
    await asyncio.sleep(0.05)  # Simular IO blocking
    logging.info(f"PUSH Enviado: Alerta {alert.level} de {alert.sensor_id}.")


# Executor para tareas que podrían ser bloqueantes (ej: acceso a DB, cálculo intensivo) [cite: 18]
executor = ThreadPoolExecutor(max_workers=5)


def blocking_data_analysis(data: SensorData) -> Optional[Alert]:
    """Simula un análisis de datos intensivo en CPU que es mejor correr en un ThreadPoolExecutor[cite: 18]."""
    sensor = SENSOR_REGISTRY.get(data.sensor_type)
    if sensor:
        # Aquí se simula el trabajo que es síncrono y bloqueante
        return sensor.process_event(data)
    return None


async def process_sensor_data_concurrently(data: SensorData, manager: ConnectionManager):
    """Función asíncrona principal para manejar el flujo del evento[cite: 37]."""

    # Ejecuta el análisis de datos (que puede ser bloqueante) en un thread separado
    # sin bloquear el loop de eventos de FastAPI/Uvicorn[cite: 18].
    loop = asyncio.get_event_loop()
    alert: Optional[Alert] = await loop.run_in_executor(
        executor,
        blocking_data_analysis,
        data
    )

    events_processed.inc()  # Métrica de eventos procesados [cite: 39, 40]

    if alert:
        logging.critical(f"¡ALERTA CRÍTICA DETECTADA! {alert.message}")

        # Envía la alerta en tiempo real a través de WebSocket [cite: 50]
        alert_message = alert.model_dump_json()
        await manager.broadcast(f"ALERTA: {alert_message}")

        # Lanza las notificaciones de forma concurrente, sin esperar la respuesta de cada una [cite: 11]
        asyncio.create_task(send_email_async(alert))
        asyncio.create_task(send_push_notification_async(alert))

    logging.info(f"Procesamiento de {data.sensor_id} finalizado.")