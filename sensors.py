# sensors.py
from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

# Modelos de Pydantic para los datos de entrada
class SensorData(BaseModel):
    sensor_type: str
    sensor_id: str
    timestamp: float
    value: Any

class Alert(BaseModel):
    sensor_id: str
    message: str
    level: str # Ej: CRITICAL, WARNING

# Clase base abstracta [cite: 30]
class BaseSensor(ABC):
    @abstractmethod
    def process_event(self, data: SensorData) -> Optional[Alert]:
        """Procesa datos del sensor y retorna una Alerta si aplica[cite: 34]."""
        pass

# Implementación de Sensores específicos [cite: 31, 32, 33]
class MotionSensor(BaseSensor):
    def process_event(self, data: SensorData) -> Optional[Alert]:
        if data.value == "MOVIMIENTO_NO_AUTORIZADO": # Ejemplo de condición crítica [cite: 19]
            return Alert(
                sensor_id=data.sensor_id,
                message="¡Movimiento no autorizado detectado! Intrusion[cite: 19].",
                level="CRITICAL"
            )
        return None

class TemperatureSensor(BaseSensor):
    def process_event(self, data: SensorData) -> Optional[Alert]:
        if isinstance(data.value, (int, float)) and data.value > 150: # Ejemplo de temperatura extrema [cite: 19]
            return Alert(
                sensor_id=data.sensor_id,
                message=f"Temperatura extrema detectada: {data.value}°C.",
                level="WARNING"
            )
        return None

class AccessSensor(BaseSensor):
    def process_event(self, data: SensorData) -> Optional[Alert]:
        if data.value == "ACCESO_DENEGADO_REPETIDO":
            return Alert(
                sensor_id=data.sensor_id,
                message="Intento de acceso denegado repetido.",
                level="WARNING"
            )
        return None

# Registro de sensores (Contenedor) [cite: 35]
SENSOR_REGISTRY: Dict[str, BaseSensor] = {
    "motion": MotionSensor(),
    "temperature": TemperatureSensor(),
    "access": AccessSensor(),
}