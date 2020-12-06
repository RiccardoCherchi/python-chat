from typing import List, Dict

from fastapi import WebSocket
from app.db.config import client # redis


class ConnectionManager:

	active_connections: Dict[ str, WebSocket ] = {}
	id_to_nick: Dict[str, str] = {}

	def __init__(self):
		pass

	async def connect(self, websocket: WebSocket, user_id: str):
		await websocket.accept()
		self.active_connections[user_id] = websocket

		client.sadd("online_users", user_id)

	def disconnect(self, websocket: WebSocket, user_id: str):
		client.srem("online_users", user_id)
		del self.active_connections[user_id]

	async def send_personal_message(self, websocket: WebSocket, message: str):
		await websocket.send_text(message)

	async def broadcast(self, message: str):
		for connection in self.active_connections.values():
			await connection.send_text(message)

	async def broadcastToEveryoneExcept(self, conn: WebSocket, message: str):
		for connection in self.active_connections.values():
			if connection != conn:
				await connection.send_text(message)
