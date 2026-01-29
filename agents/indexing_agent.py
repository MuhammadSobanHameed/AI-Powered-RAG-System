"""
Indexing Agent
Handles text chunking, embedding generation, and vector storage
"""
from typing import List, Dict
import logging
from datetime import datetime
import uuid

from config import settings
from services import embedding_service, faiss_service
from utils import chunk_text
from db import get_db_context, DocumentChunk

logger = logging.getLogger(__name__)

class IndexingAgent:
    """
    Agent responsible for indexing document content
    
    Responsibilities:
    - Split text into chunks
    - Generate embeddings
    - Store vectors in FAISS
    - Store chunk metadata in database
    """
    
    def __init__(self):
        """Initialize Indexing Agent"""
        logger.info("Indexing Agent initialized")
    
    def chunk_document_text(self, text: str, document_id: str) -> List[Dict[str, any]]:
        """
        Split document text into chunks
        
        Args:
            text: Full document text
            document_id: Document identifier
            
        Returns:
            List of chunk dictionaries
        """
        try:
            logger.info(f"Chunking text for document {document_id}")
            
            # Split text into chunks
            chunks = chunk_text(
                text,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP
            )
            
            # Create chunk objects with metadata
            chunk_objects = []
            for idx, chunk_content in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{idx}"
                chunk_objects.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": idx,
                    "content": chunk_content
                })
            
            logger.info(f"Created {len(chunk_objects)} chunks")
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}")
            return []
    
    def generate_embeddings(self, chunks: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Chunks with embeddings added
        """
        try:
            if not chunks:
                return []
            
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            
            # Extract chunk contents
            chunk_texts = [chunk["content"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = embedding_service.embed_texts(chunk_texts, show_progress=True)
            
            # Add embeddings to chunks
            for idx, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[idx]
            
            logger.info(f"Embeddings generated successfully")
            return chunks
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def store_in_vector_db(self, chunks: List[Dict[str, any]]) -> bool:
        """
        Store embeddings in FAISS vector database
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            Success status
        """
        try:
            if not chunks:
                return False
            
            logger.info(f"Storing {len(chunks)} vectors in FAISS")
            
            # Extract embeddings and chunk IDs
            embeddings = [chunk["embedding"] for chunk in chunks]
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]
            
            # Convert to numpy array
            import numpy as np
            embeddings_array = np.array(embeddings)
            
            # Add to FAISS
            faiss_service.add_vectors(embeddings_array, chunk_ids)
            
            # Persist index
            faiss_service.save_index()
            
            logger.info(f"Vectors stored successfully. Total vectors: {faiss_service.get_total_vectors()}")
            return True
            
        except Exception as e:
            logger.error(f"Vector storage failed: {str(e)}")
            return False
    
    def store_chunk_metadata(self, chunks: List[Dict[str, any]]) -> bool:
        """
        Store chunk metadata in database
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Storing metadata for {len(chunks)} chunks")
            
            with get_db_context() as db:
                for chunk in chunks:
                    db_chunk = DocumentChunk(
                        chunk_id=chunk["chunk_id"],
                        document_id=chunk["document_id"],
                        chunk_index=chunk["chunk_index"],
                        content=chunk["content"],
                        embedding_index=chunk.get("embedding_index")
                    )
                    db.add(db_chunk)
            
            logger.info("Chunk metadata stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Metadata storage failed: {str(e)}")
            return False
    
    def index_document(self, text: str, document_id: str) -> Dict[str, any]:
        """
        Complete document indexing pipeline
        
        Args:
            text: Document text
            document_id: Document identifier
            
        Returns:
            Dictionary with indexing result
        """
        try:
            logger.info(f"Starting indexing for document {document_id}")
            
            # Step 1: Chunk text
            chunks = self.chunk_document_text(text, document_id)
            if not chunks:
                return {
                    "success": False,
                    "error": "Failed to create chunks"
                }
            
            # Step 2: Generate embeddings
            chunks_with_embeddings = self.generate_embeddings(chunks)
            
            # Step 3: Store in vector database
            vector_success = self.store_in_vector_db(chunks_with_embeddings)
            if not vector_success:
                return {
                    "success": False,
                    "error": "Failed to store vectors"
                }
            
            # Step 4: Store metadata
            metadata_success = self.store_chunk_metadata(chunks_with_embeddings)
            if not metadata_success:
                return {
                    "success": False,
                    "error": "Failed to store metadata"
                }
            
            logger.info(f"Document {document_id} indexed successfully")
            return {
                "success": True,
                "num_chunks": len(chunks),
                "total_vectors": faiss_service.get_total_vectors()
            }
            
        except Exception as e:
            logger.error(f"Indexing failed: {str(e)}")
            return {
                "success": False,
                "error": f"Indexing error: {str(e)}"
            }


# Global indexing agent instance
indexing_agent = IndexingAgent()