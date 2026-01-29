"""
Text Chunking Utilities
Handles text splitting for embedding and retrieval
"""
from typing import List
from config import settings

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks for better retrieval
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP
    
    if not text or len(text) == 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk end position
        end = start + chunk_size
        
        # If not at the end, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 chars of the chunk
            search_start = max(end - 100, start)
            last_period = text.rfind('.', search_start, end)
            last_newline = text.rfind('\n', search_start, end)
            last_boundary = max(last_period, last_newline)
            
            if last_boundary > start:
                end = last_boundary + 1
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
    
    return chunks


def chunk_text_by_sentences(text: str, max_sentences: int = 5, overlap_sentences: int = 1) -> List[str]:
    """
    Alternative chunking strategy based on sentences
    
    Args:
        text: Input text to chunk
        max_sentences: Maximum sentences per chunk
        overlap_sentences: Number of sentences to overlap
        
    Returns:
        List of text chunks
    """
    # Simple sentence splitting (can be improved with NLTK)
    sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
    
    if not sentences:
        return []
    
    chunks = []
    i = 0
    
    while i < len(sentences):
        chunk_sentences = sentences[i:i + max_sentences]
        chunk = ' '.join(chunk_sentences)
        chunks.append(chunk)
        i += max_sentences - overlap_sentences
    
    return chunks