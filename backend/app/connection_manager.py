"""Tracks every currently-connected dashboard and routes events to the right
subset of them. This is the piece that makes "broadcast to managers only"
possible without the REST layer knowing anything about who's online.
"""
from fastapi import WebSocket

from app.schemas import WSEvent


class ConnectionManager:
    def __init__(self) -> None:
        # user_id -> (websocket, role). A dict, not a list, so disconnecting
        # a specific user is an O(1) delete instead of a linear scan.
        self.active_connections: dict[int, tuple[WebSocket, str]] = {}

    async def connect(self, user_id: int, role: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id] = (websocket, role)

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def broadcast(self, event: WSEvent) -> int:
        """Send to every connection whose role matches event.target_role
        ("ALL" matches everyone). Returns how many connections received it,
        which the tests use to prove role-scoping actually works.
        """
        sent = 0
        payload = event.model_dump(mode="json")
        for _user_id, (websocket, role) in list(self.active_connections.items()):
            if event.target_role == "ALL" or role == event.target_role:
                await websocket.send_json(payload)
                sent += 1
        return sent


manager = ConnectionManager()
