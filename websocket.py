# websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import logging
import json


# Manejador de conexiones WebSocket [cite: 51]
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []  # Almacena las conexiones activas

    async def connect(self, websocket: WebSocket):
        """Acepta la conexión y la añade a la lista."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"Nueva conexión WebSocket activa. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remueve la conexión desconectada."""
        self.active_connections.remove(websocket)
        logging.info(f"Conexión WebSocket cerrada. Restantes: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envía un mensaje a un cliente específico."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Difunde el mensaje (alerta) a todos los clientes conectados[cite: 51]."""
        # Se asegura de enviar solo a las conexiones que siguen activas
        inactive_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                inactive_connections.append(connection)
            except Exception as e:
                logging.error(f"Error al enviar por WebSocket a un cliente: {e}")
                inactive_connections.append(connection)

        # Elimina las conexiones inactivas
        for connection in inactive_connections:
            self.active_connections.remove(connection)

        logging.info(f"Broadcast a {len(self.active_connections)} clientes activos: {message[:50]}...")