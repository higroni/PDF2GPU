"""
Evaluation Logs WebSocket Router
Real-time log streaming for evaluation execution
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections per evaluation
active_connections: Dict[int, Set[WebSocket]] = {}


class EvaluationLogBroadcaster:
    """Broadcaster for evaluation logs"""
    
    @staticmethod
    async def connect(evaluation_id: int, websocket: WebSocket):
        """Connect a WebSocket client"""
        await websocket.accept()
        
        if evaluation_id not in active_connections:
            active_connections[evaluation_id] = set()
        
        active_connections[evaluation_id].add(websocket)
        logger.info(f"WebSocket connected for evaluation {evaluation_id}. Total connections: {len(active_connections[evaluation_id])}")
    
    @staticmethod
    def disconnect(evaluation_id: int, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if evaluation_id in active_connections:
            active_connections[evaluation_id].discard(websocket)
            
            if not active_connections[evaluation_id]:
                del active_connections[evaluation_id]
            
            logger.info(f"WebSocket disconnected for evaluation {evaluation_id}")
    
    @staticmethod
    async def broadcast_log(evaluation_id: int, level: str, message: str):
        """Broadcast a log message to all connected clients"""
        if evaluation_id not in active_connections:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in active_connections[evaluation_id]:
            try:
                await websocket.send_text(json.dumps(log_entry))
            except Exception as e:
                logger.error(f"Error sending log to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            active_connections[evaluation_id].discard(websocket)


# Global broadcaster instance
log_broadcaster = EvaluationLogBroadcaster()


@router.websocket("/ws/evaluation/{evaluation_id}/logs")
async def evaluation_logs_websocket(websocket: WebSocket, evaluation_id: int):
    """
    WebSocket endpoint for real-time evaluation logs
    
    Args:
        websocket: WebSocket connection
        evaluation_id: ID of the evaluation
    """
    await log_broadcaster.connect(evaluation_id, websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "INFO",
            "message": f"Povezano na log stream za evaluaciju {evaluation_id}"
        }))
        
        # Keep connection alive and listen for client messages (if any)
        while True:
            try:
                # Wait for any message from client (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Echo back to keep connection alive
                if data == "ping":
                    await websocket.send_text(json.dumps({
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "level": "DEBUG",
                        "message": "pong"
                    }))
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_text(json.dumps({
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "level": "DEBUG",
                        "message": "keepalive"
                    }))
                except:
                    break
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for evaluation {evaluation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for evaluation {evaluation_id}: {e}")
    finally:
        log_broadcaster.disconnect(evaluation_id, websocket)


# Export broadcaster for use in evaluation service
__all__ = ['router', 'log_broadcaster']

# Made with Bob