"""
QA Agent
Handles question answering using retrieval-augmented generation
"""
from typing import List, Dict, Optional
import logging

from config import settings
from services import embedding_service, faiss_service, get_llm_service
from db import get_db_context, DocumentChunk

logger = logging.getLogger(__name__)

class QAAgent:
    """
    Agent responsible for answering questions based on document content
    
    Responsibilities:
    - Embed user queries
    - Retrieve relevant chunks from FAISS
    - Construct context from retrieved chunks
    - Generate answers using LLM
    """
    
    def __init__(self):
        """Initialize QA Agent"""
        logger.info("QA Agent initialized")
    
    def embed_question(self, question: str):
        """
        Generate embedding for user question
        
        Args:
            question: User question
            
        Returns:
            Question embedding
        """
        try:
            logger.info(f"Embedding question: {question[:100]}...")
            embedding = embedding_service.embed_text(question)
            return embedding
        except Exception as e:
            logger.error(f"Question embedding failed: {str(e)}")
            raise
    
    def retrieve_relevant_chunks(self, question_embedding, k: int = None) -> List[str]:
        """
        Retrieve relevant chunks from vector database
        
        Args:
            question_embedding: Embedded question
            k: Number of chunks to retrieve
            
        Returns:
            List of chunk IDs
        """
        try:
            if k is None:
                k = settings.TOP_K_RESULTS
            
            logger.info(f"Retrieving top {k} relevant chunks")
            
            # Search FAISS
            distances, chunk_ids = faiss_service.search(question_embedding, k=k)
            
            if not chunk_ids:
                logger.warning("No relevant chunks found")
                return []
            
            logger.info(f"Retrieved {len(chunk_ids)} chunks")
            logger.debug(f"Distances: {distances}")
            
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Chunk retrieval failed: {str(e)}")
            return []
    
    def get_chunk_contents(self, chunk_ids: List[str]) -> List[Dict[str, any]]:
        """
        Fetch chunk contents from database
        
        Args:
            chunk_ids: List of chunk identifiers
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        try:
            logger.info(f"Fetching content for {len(chunk_ids)} chunks")
            
            chunks = []
            with get_db_context() as db:
                for chunk_id in chunk_ids:
                    db_chunk = db.query(DocumentChunk).filter(
                        DocumentChunk.chunk_id == chunk_id
                    ).first()
                    
                    if db_chunk:
                        chunks.append({
                            "chunk_id": db_chunk.chunk_id,
                            "document_id": db_chunk.document_id,
                            "content": db_chunk.content,
                            "chunk_index": db_chunk.chunk_index
                        })
            
            logger.info(f"Fetched {len(chunks)} chunk contents")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to fetch chunk contents: {str(e)}")
            return []
    
    def construct_context(self, chunks: List[Dict[str, any]]) -> str:
        """
        Construct context string from retrieved chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        # Sort chunks by document and chunk index for coherence
        sorted_chunks = sorted(chunks, key=lambda x: (x["document_id"], x["chunk_index"]))
        
        # Build context
        context_parts = []
        current_doc = None
        
        for chunk in sorted_chunks:
            # Add document separator if new document
            if chunk["document_id"] != current_doc:
                if current_doc is not None:
                    context_parts.append("\n---\n")
                context_parts.append(f"[Source]\n")
                current_doc = chunk["document_id"]
            
            context_parts.append(chunk["content"])
            context_parts.append("\n\n")
        
        context = "".join(context_parts).strip()
        logger.info(f"Constructed context with {len(context)} characters")
        
        return context
    
    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        try:
            logger.info("Generating answer with LLM")
            
            llm_service = get_llm_service()
            answer = llm_service.generate_answer_from_context(question, context)
            
            logger.info(f"Answer generated: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            return "I apologize, but I encountered an error while generating the answer."
    
    def answer_question(self, question: str) -> Dict[str, any]:
        """
        Complete question answering pipeline
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Step 1: Embed question
            question_embedding = self.embed_question(question)
            
            # Step 2: Retrieve relevant chunks
            chunk_ids = self.retrieve_relevant_chunks(question_embedding)
            
            if not chunk_ids:
                return {
                    "success": True,
                    "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Step 3: Get chunk contents
            chunks = self.get_chunk_contents(chunk_ids)
            
            if not chunks:
                return {
                    "success": True,
                    "answer": "I found relevant chunks but couldn't retrieve their content. Please try again.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Step 4: Construct context
            context = self.construct_context(chunks)
            
            # Step 5: Generate answer
            answer = self.generate_answer(question, context)
            
            # Extract unique document IDs
            source_docs = list(set([chunk["document_id"] for chunk in chunks]))
            
            return {
                "success": True,
                "answer": answer,
                "sources": source_docs,
                "num_sources": len(source_docs),
                "num_chunks_used": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Question answering failed: {str(e)}")
            return {
                "success": False,
                "error": f"QA error: {str(e)}"
            }


# Global QA agent instance
qa_agent = QAAgent()