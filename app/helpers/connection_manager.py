from fastapi import WebSocket
from app.db.config import client # redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)

        client.sadd("online_users", user_id)

    def disconnect(self, websocket: WebSocket, user_id: str):
        client.srem("online_users", user_id)
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
