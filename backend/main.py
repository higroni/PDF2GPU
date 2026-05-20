"""
PDF2GPU FastAPI Application
Main entry point
"""
import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db
from backend.routers import collections_router, pdfs_router, search_router
from backend.routers.chat import router as chat_router
from backend.routers.test_examples import router as test_examples_router
from backend.routers.evaluations import router as evaluations_router
from backend.dependencies import get_rag_engine

# Setup logging with ASCII encoding
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8',
    errors='replace'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF2GPU API",
    description="RAG sistem sa GPU optimizacijom za obradu PDF dokumenata",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler za detaljno logovanje grešaka."""
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )

# Include routers
app.include_router(collections_router, prefix="/api")
app.include_router(pdfs_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(test_examples_router)
app.include_router(evaluations_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "PDF2GPU API is running"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF2GPU API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Inicijalizacija pri pokretanju"""
    logger.info("Starting PDF2GPU API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("PDF2GPU API started successfully")
    logger.info("RAG Engine will be initialized on first use")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup pri gašenju"""
    logger.info("Shutting down PDF2GPU API...")
    
    # Cleanup RAG Engine
    try:
        rag_engine = get_rag_engine()
        rag_engine.clear_cache()
        logger.info("RAG Engine cache cleared")
    except:
        pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF2GPU API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )

# Made with Bob
