"""
Chat Router
WebSocket i HTTP endpoints za chat funkcionalnost
"""
import logging
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.chat_service import ChatService
from backend.websocket import manager, handle_websocket_message
from backend.dependencies import get_rag_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Dependency za ChatService"""
    return ChatService(db)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint za real-time chat
    
    Message format (client -> server):
    {
        "type": "query" | "ping" | "disconnect",
        "content": str,
        "collection_id": int (optional),
        "use_context": bool (optional, default: true)
    }
    
    Message format (server -> client):
    {
        "type": "status" | "context" | "token" | "complete" | "error" | "pong",
        "content": any
    }
    """
    await manager.connect(websocket, session_id)
    chat_service = ChatService(db)
    
    try:
        # Dohvati postojeću sesiju (već kreirana preko POST /sessions)
        session_id_int = int(session_id)
        
        # Pošalji status da je konekcija uspešna
        await manager.send_status(session_id, "Povezan")
        
        while True:
            # Primi poruku sa timeout-om od 25s (frontend šalje ping svakih 20s)
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=25.0)
            except asyncio.TimeoutError:
                # Ako nema poruke 25s, pošalji ping da održimo konekciju
                await manager.send_message(session_id, {"type": "ping", "content": "keepalive"})
                continue
            
            message_type = data.get("type")
            
            if message_type == "query":
                # Obradi query
                query = data.get("content", "")
                collection_id = data.get("collection_id")
                use_context = data.get("use_context", True)
                
                if not query:
                    await manager.send_error(session_id, "Query ne može biti prazan")
                    continue
                
                try:
                    # Stream odgovor
                    async for response in chat_service.generate_response(
                        session_id_int,
                        query,
                        collection_id,
                        use_context
                    ):
                        await manager.send_message(session_id, response)
                
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    await manager.send_error(session_id, f"Greška: {str(e)}")
            
            else:
                # Ostale poruke (ping, disconnect, etc.)
                await handle_websocket_message(websocket, session_id, data)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        manager.disconnect(session_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        await manager.send_error(session_id, f"Greška: {str(e)}")
        manager.disconnect(session_id)


@router.post("/sessions")
async def create_session(
    collection_id: int = None,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Kreiraj novu chat sesiju"""
    try:
        session = await chat_service.create_session(collection_id)
        return {
            "id": session.id,
            "session_id": session.id,  # Za kompatibilnost
            "collection_id": session.collection_id,
            "started_at": session.started_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Dohvati sve poruke iz sesije"""
    try:
        messages = await chat_service.get_session_messages(session_id)
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": str(msg.role),
                    "content": str(msg.content),
                    "metadata": msg.message_metadata,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def end_session(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Završi chat sesiju"""
    try:
        await chat_service.end_session(session_id)
        return {"message": "Sesija završena", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-sessions")
async def get_active_sessions():
    """Dohvati listu aktivnih WebSocket sesija"""
    return {
        "active_sessions": manager.get_active_sessions()
    }


# Made with Bob