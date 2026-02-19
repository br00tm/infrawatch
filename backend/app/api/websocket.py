"""WebSocket connection manager and handlers."""

import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected", total=len(self.active_connections))

    async def broadcast(self, event_type: str, data: Any):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps({"type": event_type, "data": data})
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws)

    async def send_to(self, websocket: WebSocket, event_type: str, data: Any):
        """Send a message to a single client."""
        message = json.dumps({"type": event_type, "data": data})
        await websocket.send_text(message)


# Global manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint handler."""
    await manager.connect(websocket)
    try:
        # Send initial connection confirmation
        await manager.send_to(websocket, "connected", {"message": "Connected to InfraWatch"})

        # Keep connection alive, listening for client messages
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle ping
                if msg.get("type") == "ping":
                    await manager.send_to(websocket, "pong", {})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)
