"""
WebSocket Manager
Upravljanje WebSocket konekcijama za real-time chat
"""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manager za WebSocket konekcije"""
    
    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Session metadata
        self.session_metadata: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Prihvati novu WebSocket konekciju"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_metadata[session_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "message_count": 0
        }
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Diskonektuj WebSocket konekciju"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """Pošalji poruku određenoj sesiji"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
                self.session_metadata[session_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_text(self, session_id: str, text: str):
        """Pošalji text poruku"""
        await self.send_message(session_id, {"type": "text", "content": text})
    
    async def send_error(self, session_id: str, error: str):
        """Pošalji error poruku"""
        await self.send_message(session_id, {"type": "error", "content": error})
    
    async def send_status(self, session_id: str, status: str):
        """Pošalji status update"""
        await self.send_message(session_id, {"type": "status", "content": status})
    
    async def stream_token(self, session_id: str, token: str):
        """Stream pojedinačni token (za LLM streaming)"""
        await self.send_message(session_id, {"type": "token", "content": token})
    
    async def stream_complete(self, session_id: str):
        """Signaliziraj kraj streaming-a"""
        await self.send_message(session_id, {"type": "stream_complete"})
    
    def get_active_sessions(self) -> list:
        """Dohvati listu aktivnih sesija"""
        return [
            {
                "session_id": session_id,
                **metadata
            }
            for session_id, metadata in self.session_metadata.items()
        ]
    
    def is_connected(self, session_id: str) -> bool:
        """Proveri da li je sesija aktivna"""
        return session_id in self.active_connections


# Global instance
manager = ConnectionManager()


async def handle_websocket_message(
    websocket: WebSocket,
    session_id: str,
    message: dict
):
    """
    Obradi primljenu WebSocket poruku
    
    Message format:
    {
        "type": "query" | "ping" | "disconnect",
        "content": str,
        "metadata": dict (optional)
    }
    """
    message_type = message.get("type")
    content = message.get("content", "")
    
    if message_type == "ping":
        # Heartbeat
        await manager.send_message(session_id, {"type": "pong"})
    
    elif message_type == "disconnect":
        # Graceful disconnect
        await manager.send_message(session_id, {"type": "disconnected"})
        manager.disconnect(session_id)
    
    elif message_type == "query":
        # Query će biti obrađen u chat endpoint-u
        # Ovde samo logujemo
        logger.info(f"Query received from {session_id}: {content[:50]}...")
    
    else:
        logger.warning(f"Unknown message type from {session_id}: {message_type}")
        await manager.send_error(session_id, f"Unknown message type: {message_type}")


# Made with Bob