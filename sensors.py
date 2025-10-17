from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class SensorData(BaseModel):
    sensor_type: str
    sensor_id: str
    timestamp: float
    value: Any

class Alert(BaseModel):
    sensor_id: str
    message: str
    level: str

class BaseSensor(ABC):
    @abstractmethod
    def process_event(self, data: SensorData) -> Optional[Alert]:
        pass

class MotionSensor(BaseSensor):
    def process_event(self, data: SensorData) -> Optional[Alert]:
        if data.value == "MOVIMIENTO_NO_AUTORIZADO":
            return Alert(
                sensor_id=data.sensor_id,
                message="¡Movimiento no autorizado detectado! Intrusion[cite: 19].",
                level="CRITICAL"
            )
        return None

class TemperatureSensor(BaseSensor):
    def process_event(self, data: SensorData) -> Optional[Alert]:
        if isinstance(data.value, (int, float)) and data.value > 150:
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

SENSOR_REGISTRY: Dict[str, BaseSensor] = {
    "motion": MotionSensor(),
    "temperature": TemperatureSensor(),
    "access": AccessSensor(),
}