"""
Embedding Service
Handles text embedding generation using Sentence Transformers
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

from config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings from text using Sentence Transformers
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding service
        
        Args:
            model_name: Name of the Sentence Transformer model
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded. Dimension: {self.embedding_dim}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            
        Returns:
            Array of embedding vectors
        """
        try:
            if not texts:
                return np.array([])
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model
        
        Returns:
            Embedding dimension
        """
        return self.embedding_dim
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        from numpy.linalg import norm
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))
        return float(similarity)


# Global embedding service instance
embedding_service = EmbeddingService()