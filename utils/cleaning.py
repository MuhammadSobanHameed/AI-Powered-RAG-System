"""
Text Cleaning Utilities
Handles text normalization and cleanup
"""
import re
from typing import Optional

def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'([.!?]){2,}', r'\1', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    return text.strip()


def remove_page_numbers(text: str) -> str:
    """
    Remove common page number patterns from text
    
    Args:
        text: Input text
        
    Returns:
        Text with page numbers removed
    """
    # Remove standalone numbers that look like page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
    
    return text


def extract_meaningful_text(text: str, min_length: int = 50) -> Optional[str]:
    """
    Extract meaningful text, filtering out very short or empty content
    
    Args:
        text: Input text
        min_length: Minimum length for meaningful text
        
    Returns:
        Cleaned text if meaningful, None otherwise
    """
    cleaned = clean_text(text)
    
    if len(cleaned) < min_length:
        return None
    
    # Check if text has reasonable word count
    words = cleaned.split()
    if len(words) < 5:
        return None
    
    return cleaned