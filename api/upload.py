"""
Document Upload API Endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging

from agents import ingestion_agent, indexing_agent
from db import get_db, Document
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    status: str
    message: Optional[str] = None
    num_chunks: Optional[int] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document (PDF or Image)
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts text using OCR or PDF parsing
    3. Chunks the text and generates embeddings
    4. Stores vectors in FAISS for retrieval
    
    Args:
        file: Uploaded file (PDF or Image)
        db: Database session
        
    Returns:
        Document metadata and processing status
    """
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
        # Generate unique document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Read file data
        file_data = await file.read()
        file_size = len(file_data)
        
        logger.info(f"File size: {file_size} bytes")
        
        # Create database entry
        db_document = Document(
            document_id=document_id,
            filename=file.filename,
            file_path="",  # Will be updated after saving
            file_type=file.content_type or "unknown",
            file_size=file_size,
            status="processing"
        )
        db.add(db_document)
        db.commit()
        
        # Step 1: Ingestion - Process document and extract text
        logger.info(f"Starting ingestion for document {document_id}")
        ingestion_result = ingestion_agent.process_document(
            file_data=file_data,
            filename=file.filename,
            document_id=document_id
        )
        
        if not ingestion_result["success"]:
            db_document.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=ingestion_result.get("error", "Ingestion failed")
            )
        
        # Update file path
        db_document.file_path = ingestion_result["file_path"]
        db.commit()
        
        # Step 2: Indexing - Chunk text, generate embeddings, store in FAISS
        logger.info(f"Starting indexing for document {document_id}")
        indexing_result = indexing_agent.index_document(
            text=ingestion_result["extracted_text"],
            document_id=document_id
        )
        
        if not indexing_result["success"]:
            db_document.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=500,
                detail=indexing_result.get("error", "Indexing failed")
            )
        
        # Update document status
        db_document.status = "indexed"
        db_document.indexed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Document {document_id} processed successfully")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="indexed",
            message="Document processed and indexed successfully",
            num_chunks=indexing_result.get("num_chunks")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        if db_document:
            db_document.status = "failed"
            db.commit()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/status/{document_id}")
async def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """
    Get the processing status of a document
    
    Args:
        document_id: Document identifier
        db: Database session
        
    Returns:
        Document status information
    """
    document = db.query(Document).filter(Document.document_id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "status": document.status,
        "created_at": document.created_at.isoformat(),
        "indexed_at": document.indexed_at.isoformat() if document.indexed_at else None
    }