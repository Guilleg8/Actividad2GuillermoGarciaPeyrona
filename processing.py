import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Set

from sensors import SensorData, SENSOR_REGISTRY, Alert
from websocket import ConnectionManager
from metrics import events_processed
from metrics import events_processed

background_tasks: Set[asyncio.Task] = set()

async def send_email_async(alert: Alert):
    await asyncio.sleep(0.05)
    logging.info(f"EMAIL Enviado: Alerta {alert.level} de {alert.sensor_id}.")


async def send_push_notification_async(alert: Alert):
    await asyncio.sleep(0.05)
    logging.info(f"PUSH Enviado: Alerta {alert.level} de {alert.sensor_id}.")


executor = ThreadPoolExecutor(max_workers=5)


def blocking_data_analysis(data: SensorData) -> Optional[Alert]:
    sensor = SENSOR_REGISTRY.get(data.sensor_type)
    if sensor:
        return sensor.process_event(data)
    return None


# ... (otras funciones e importaciones) ...
# ... (background_tasks = set() ) ...

async def process_sensor_data_concurrently(data: SensorData, manager: ConnectionManager):
    loop = asyncio.get_event_loop()
    alert: Optional[Alert] = await loop.run_in_executor(
        executor,
        blocking_data_analysis,
        data
    )

    events_processed.inc()

    if alert:  # <-- EL 'IF' ES CLAVE
        # TODO ESTE BLOQUE DEBE ESTAR INDENTADO DENTRO DEL 'if alert:'
        logging.critical(f"¡ALERTA CRÍTICA DETECTADA! {alert.message}")

        alert_message = alert.model_dump_json()
        await manager.broadcast(f"ALERTA: {alert_message}")

        # Crea las tareas y guárdalas en variables
        email_task = asyncio.create_task(send_email_async(alert))
        push_task = asyncio.create_task(send_push_notification_async(alert))

        # Añade las tareas al conjunto global
        background_tasks.add(email_task)
        background_tasks.add(push_task)

        # Añade callbacks para limpiar el conjunto cuando terminen
        email_task.add_done_callback(background_tasks.discard)
        push_task.add_done_callback(background_tasks.discard)
        # --- FIN DEL BLOQUE INDENTADO ---

    logging.info(f"Procesamiento de {data.sensor_id} finalizado.")