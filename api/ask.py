"""
Question Answering API Endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from agents import qa_agent

logger = logging.getLogger(__name__)

router = APIRouter()

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=1, description="Question to ask about uploaded documents")
    max_sources: Optional[int] = Field(5, description="Maximum number of document chunks to retrieve")


class QuestionResponse(BaseModel):
    """Response model for question answering"""
    answer: str
    sources: List[str]
    num_sources: int
    confidence: Optional[str] = "medium"


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question based on uploaded documents
    
    This endpoint:
    1. Embeds the user's question
    2. Retrieves relevant chunks from FAISS
    3. Constructs context from retrieved chunks
    4. Generates an answer using LLM (Groq LLaMA)
    
    The answer is grounded strictly in the uploaded document content.
    
    Args:
        request: Question request containing the user's question
        
    Returns:
        Answer with source document references
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Validate question
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Process question through QA agent
        result = qa_agent.answer_question(request.question)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate answer")
            )
        
        # Determine confidence based on number of sources
        confidence = "high" if result["num_sources"] >= 3 else "medium" if result["num_sources"] >= 1 else "low"
        
        logger.info(f"Question answered successfully with {result['num_sources']} sources")
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_sources=result["num_sources"],
            confidence=confidence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question answering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        API status
    """
    return {
        "status": "healthy",
        "service": "Document Intelligence QA API"
    }