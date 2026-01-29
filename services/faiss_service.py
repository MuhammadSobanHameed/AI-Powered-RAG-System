"""
FAISS Service
Handles vector storage and similarity search using FAISS
"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

class FAISSService:
    """
    Service for managing FAISS vector index
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS service
        
        Args:
            dimension: Dimension of embedding vectors
        """
        self.dimension = dimension
        self.index = None
        self.index_path = settings.FAISS_DIR / "document_index.faiss"
        self.metadata_path = settings.FAISS_DIR / "document_metadata.pkl"
        self.metadata = []  # Stores chunk_ids corresponding to vectors
        
        # Try to load existing index
        if self.index_path.exists():
            self.load_index()
        else:
            self.create_index()
    
    def create_index(self):
        """
        Create a new FAISS index
        """
        logger.info(f"Creating new FAISS index with dimension {self.dimension}")
        # Using IndexFlatL2 for exact search (good for small-medium datasets)
        # For larger datasets, consider IndexIVFFlat or IndexHNSWFlat
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info("FAISS index created successfully")
    
    def add_vectors(self, embeddings: np.ndarray, chunk_ids: List[str]):
        """
        Add vectors to the index
        
        Args:
            embeddings: Array of embedding vectors
            chunk_ids: List of chunk IDs corresponding to embeddings
        """
        if self.index is None:
            self.create_index()
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(chunk_ids)
        
        logger.info(f"Added {len(chunk_ids)} vectors to FAISS index. Total: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[float], List[str]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            Tuple of (distances, chunk_ids)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty, cannot perform search")
            return [], []
        
        # Ensure query is 2D and float32
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Limit k to available vectors
        k = min(k, self.index.ntotal)
        
        # Perform search
        distances, indices = self.index.search(query_embedding, k)
        
        # Get chunk IDs for results
        result_chunk_ids = [self.metadata[idx] for idx in indices[0] if idx < len(self.metadata)]
        result_distances = distances[0].tolist()
        
        logger.info(f"Search returned {len(result_chunk_ids)} results")
        return result_distances, result_chunk_ids
    
    def save_index(self):
        """
        Persist FAISS index and metadata to disk
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"FAISS index saved to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise
    
    def load_index(self):
        """
        Load FAISS index and metadata from disk
        """
        try:
            if self.index_path.exists() and self.metadata_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_path))
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"FAISS index loaded with {self.index.ntotal} vectors")
            else:
                logger.info("No existing index found, creating new one")
                self.create_index()
                
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            self.create_index()
    
    def get_total_vectors(self) -> int:
        """
        Get total number of vectors in index
        
        Returns:
            Number of vectors
        """
        return self.index.ntotal if self.index else 0
    
    def reset_index(self):
        """
        Reset the index (delete all vectors)
        """
        logger.info("Resetting FAISS index")
        self.create_index()
        self.save_index()


# Global FAISS service instance
faiss_service = FAISSService()