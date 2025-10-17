from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import logging
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"Nueva conexión WebSocket activa. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logging.info(f"Conexión WebSocket cerrada. Restantes: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        inactive_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                inactive_connections.append(connection)
            except Exception as e:
                logging.error(f"Error al enviar por WebSocket a un cliente: {e}")
                inactive_connections.append(connection)

        for connection in inactive_connections:
            self.active_connections.remove(connection)

        logging.info(f"Broadcast a {len(self.active_connections)} clientes activos: {message[:50]}...")