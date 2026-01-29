"""
Main FastAPI Application
Entry point for the AI-Powered RAG System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from config import settings
from db import init_db
from api import upload, ask

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting AI-Powered RAG System...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"FAISS directory: {settings.FAISS_DIR}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Load or initialize FAISS index
    from services import faiss_service
    logger.info(f"FAISS index loaded with {faiss_service.get_total_vectors()} vectors")
    
    # Verify Groq API key
    if settings.GROQ_API_KEY:
        logger.info("✅ Groq API key configured")
    else:
        logger.warning("⚠️  Groq API key not found. QA functionality will not work.")
    
    logger.info("🚀 Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI-Powered RAG System...")
    logger.info("👋 Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI-Powered RAG System",
    description="""
    AI-powered document intelligence system with multi-agent architecture.
    
    ## Features
    - Upload PDF and image documents
    - Automatic text extraction (OCR for images)
    - Vector-based semantic search
    - Question answering grounded in document content
    
    ## Architecture
    - **Ingestion Agent**: Processes and extracts text from documents
    - **Indexing Agent**: Chunks text, generates embeddings, stores in FAISS
    - **QA Agent**: Retrieves relevant context and generates answers
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    upload.router,
    prefix="/documents",
    tags=["Document Management"]
)

app.include_router(
    ask.router,
    prefix="/documents",
    tags=["Question Answering"]
)

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "service": "AI-Powered RAG System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/documents/upload",
            "ask": "/documents/ask",
            "health": "/documents/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    from services import faiss_service
    
    return {
        "status": "healthy",
        "database": "connected",
        "vector_db": {
            "status": "connected",
            "total_vectors": faiss_service.get_total_vectors()
        },
        "groq_api": "configured" if settings.GROQ_API_KEY else "not_configured"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )