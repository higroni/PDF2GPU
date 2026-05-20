"""
Chat Service
Servis za chat funkcionalnost sa LLM integracijom
"""
import logging
import json
from typing import Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session
import httpx

from backend.models.chat_message import ChatMessage
from backend.models.session_log import SessionLog
from backend.config import settings
from backend.services.search_service import SearchService
from backend.dependencies import get_rag_engine

logger = logging.getLogger(__name__)


class ChatService:
    """Servis za chat i LLM integraciju"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        # Inicijalizuj SearchService za dohvatanje konteksta
        self.search_service = SearchService(get_rag_engine())
    
    async def create_session(self, collection_id: Optional[int] = None) -> SessionLog:
        """Kreiraj novu chat sesiju"""
        session = SessionLog(
            collection_id=collection_id,
            started_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info(f"Created chat session: {session.id}")
        return session
    
    async def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
        message_metadata: Optional[dict] = None
    ) -> ChatMessage:
        """Sačuvaj chat poruku"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=message_metadata,
            timestamp=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def get_session_messages(self, session_id: int) -> list[ChatMessage]:
        """Dohvati sve poruke iz sesije"""
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
            .all()
        )
    
    async def get_context_for_query(
        self,
        query: str,
        collection_id: Optional[int] = None,
        top_k: int = 5
    ) -> tuple[str, list]:
        """Dohvati kontekst iz dokumenata za query"""
        try:
            # Koristi SearchService za dohvatanje konteksta
            result = self.search_service.search(
                db=self.db,
                query=query,
                collection_id=collection_id,
                top_k=top_k,
                use_reranking=True
            )
            
            logger.info(f"Search result keys: {result.keys()}")
            logger.info(f"Number of results: {len(result.get('results', []))}")
            
            # Formatiraj kontekst iz rezultata
            context_parts = []
            sources = []
            
            results = result.get('results', [])
            if not results:
                logger.warning(f"No results found for query: {query}")
                return "", []
            
            for idx, res in enumerate(results, 1):
                logger.info(f"Result {idx} keys: {res.keys() if isinstance(res, dict) else type(res)}")
                
                # Rezultati iz RAG Engine imaju strukturu: {id, score, payload: {text, metadata}}
                payload = res.get('payload', {}) if isinstance(res, dict) else {}
                logger.info(f"Result {idx} payload keys: {payload.keys() if isinstance(payload, dict) else type(payload)}")
                
                chunk_text = payload.get('text', '')
                metadata = payload.get('metadata', {})
                
                filename = metadata.get('filename', 'Unknown')
                page = metadata.get('page_number', '?')
                
                logger.info(f"Result {idx}: text_len={len(chunk_text)}, filename={filename}, page={page}")
                
                if chunk_text:
                    context_parts.append(
                        f"[Izvor {idx}: {filename}, strana {page}]\n{chunk_text}\n"
                    )
                    
                    # Dodaj source info
                    sources.append({
                        'filename': filename,
                        'page_number': page,
                        'score': res.get('combined_score', res.get('score', 0)),
                        'text': chunk_text[:200] + '...' if len(chunk_text) > 200 else chunk_text
                    })
            
            context = "\n".join(context_parts)
            logger.info(f"Context length: {len(context)} chars, {len(sources)} sources")
            return context, sources
            
        except Exception as e:
            logger.error(f"Error getting context: {e}", exc_info=True)
            # Ako nema kolekcije ili greška, vrati prazan kontekst
            return "", []
    
    def build_prompt(
        self,
        query: str,
        context: str,
        chat_history: list[ChatMessage]
    ) -> str:
        """Konstruiši prompt za LLM"""
        # System prompt
        system_prompt = """Ti si AI asistent specijalizovan za analizu pravnih dokumenata.
Tvoj zadatak je da odgovaraš na pitanja korisnika na osnovu dostavljenog konteksta iz dokumenata.

Pravila:
1. Odgovaraj SAMO na osnovu informacija iz konteksta
2. Ako informacija nije u kontekstu, jasno reci da ne znaš
3. Budi precizan i koncizan
4. Koristi srpski jezik (latinica)
5. Citiraj relevantne delove dokumenata kada je moguće
"""
        
        # Chat history
        history_text = ""
        if chat_history:
            history_text = "\n\nPrethodna konverzacija:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "Korisnik" if str(msg.role) == "user" else "Asistent"
                history_text += f"{role}: {str(msg.content)}\n"
        
        # Context
        context_text = f"\n\nKontekst iz dokumenata:\n{context}\n" if context else ""
        
        # Final prompt
        prompt = f"""{system_prompt}{history_text}{context_text}

Korisnik: {query}

Asistent:"""
        
        return prompt
    
    async def stream_llm_response(
        self,
        prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream LLM odgovor token po token"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": settings.LLM_TEMPERATURE,
                            "top_p": settings.LLM_TOP_P,
                            "top_k": settings.LLM_TOP_K,
                        }
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error streaming LLM response: {e}")
            yield f"\n\n[Greška: {str(e)}]"
    
    async def generate_response(
        self,
        session_id: int,
        query: str,
        collection_id: Optional[int] = None,
        use_context: bool = True
    ) -> AsyncGenerator[dict, None]:
        """
        Generiši odgovor na query sa streaming-om
        
        Yields:
            dict sa tipom i sadržajem:
            - {"type": "status", "content": "..."}
            - {"type": "context", "content": {...}}
            - {"type": "token", "content": "..."}
            - {"type": "complete", "content": "..."}
        """
        try:
            # Sačuvaj user poruku
            await self.save_message(session_id, "user", query)
            
            # Dohvati kontekst ako je potreban
            context = ""
            sources = []
            logger.info(f"use_context={use_context}, collection_id={collection_id}")
            if use_context:
                yield {"type": "status", "content": "Pretražujem dokumente..."}
                logger.info(f"Calling get_context_for_query for: {query[:50]}")
                try:
                    context, sources = await self.get_context_for_query(
                        query, collection_id
                    )
                    logger.info(f"Got context: {len(context)} chars, {len(sources)} sources")
                except Exception as e:
                    logger.error(f"Exception in get_context_for_query: {e}", exc_info=True)
                    context, sources = "", []
                yield {
                    "type": "context",
                    "content": {
                        "context": context,
                        "sources": sources  # sources je već formatiran kao lista dict-ova
                    }
                }
            
            # Dohvati chat history
            yield {"type": "status", "content": "Generišem odgovor..."}
            chat_history = await self.get_session_messages(session_id)
            
            # Konstruiši prompt
            prompt = self.build_prompt(query, context, chat_history[:-1])
            
            # Stream LLM response
            full_response = ""
            async for token in self.stream_llm_response(prompt):
                full_response += token
                yield {"type": "token", "content": token}
            
            # Sačuvaj assistant poruku
            await self.save_message(
                session_id,
                "assistant",
                full_response,
                message_metadata={
                    "sources": sources if sources else None,  # sources je već lista dict-ova
                    "context_used": bool(context)
                }
            )
            
            yield {"type": "complete", "content": full_response}
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            yield {"type": "error", "content": str(e)}
    
    async def generate_answer(
        self,
        query: str,
        collection_id: Optional[int] = None,
        session_id: Optional[str] = None,
        return_metrics: bool = False
    ) -> str | dict:
        """
        Generiši odgovor na query bez streaming-a (za evaluaciju)
        
        Args:
            query: Pitanje
            collection_id: ID kolekcije za RAG
            session_id: ID sesije (opciono, za evaluaciju)
            return_metrics: Ako je True, vraća dict sa odgovorom i performance metrikama
            
        Returns:
            Generisani odgovor kao string ili dict sa metrikama
        """
        import time
        
        try:
            total_start = time.time()
            
            # Query processing
            query_start = time.time()
            # Ovde bi išla query preprocessing logika (spell check, transliteration, etc.)
            query_processing_ms = (time.time() - query_start) * 1000
            
            # Search + Reranking
            context = ""
            search_ms = 0
            reranking_ms = 0
            
            if collection_id:
                search_start = time.time()
                # get_context_for_query interno poziva search i reranking
                # Za sada merimo ukupno vreme, kasnije možemo razdvojiti
                context, _ = await self.get_context_for_query(query, collection_id)
                total_search_time = (time.time() - search_start) * 1000
                # Aproksimacija: 70% search, 30% reranking
                search_ms = total_search_time * 0.7
                reranking_ms = total_search_time * 0.3
            
            # Konstruiši prompt (bez chat history za evaluaciju)
            prompt = self.build_prompt(query, context, [])
            
            # LLM generation
            llm_start = time.time()
            full_response = ""
            async for token in self.stream_llm_response(prompt):
                full_response += token
            llm_generation_ms = (time.time() - llm_start) * 1000
            
            total_latency_ms = (time.time() - total_start) * 1000
            
            answer = full_response.strip()
            
            if return_metrics:
                return {
                    "answer": answer,
                    "metrics": {
                        "query_processing_ms": query_processing_ms,
                        "search_ms": search_ms,
                        "reranking_ms": reranking_ms,
                        "llm_generation_ms": llm_generation_ms,
                        "total_latency_ms": total_latency_ms
                    }
                }
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            error_msg = f"[Greška: {str(e)}]"
            if return_metrics:
                return {
                    "answer": error_msg,
                    "metrics": {
                        "query_processing_ms": 0,
                        "search_ms": 0,
                        "reranking_ms": 0,
                        "llm_generation_ms": 0,
                        "total_latency_ms": 0
                    }
                }
            return error_msg
    
    async def end_session(self, session_id: int):
        """Završi chat sesiju"""
        session = self.db.query(SessionLog).filter(SessionLog.id == session_id).first()
        if session:
            session.ended_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Ended chat session: {session_id}")


# Made with Bob