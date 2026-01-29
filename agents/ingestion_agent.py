"""
Ingestion Agent
Handles document upload, validation, and text extraction
"""
from pathlib import Path
from typing import Optional, Dict
import logging
import shutil

from config import settings
from services import ocr_service, pdf_service
from utils import clean_text, remove_page_numbers, extract_meaningful_text

logger = logging.getLogger(__name__)

class IngestionAgent:
    """
    Agent responsible for ingesting documents and extracting raw text
    
    Responsibilities:
    - Validate file type and size
    - Store uploaded files
    - Extract text from PDFs
    - Perform OCR on images
    - Clean and normalize text
    """
    
    def __init__(self):
        """Initialize Ingestion Agent"""
        self.upload_dir = settings.UPLOAD_DIR
        logger.info("Ingestion Agent initialized")
    
    def validate_file(self, filename: str, file_size: int) -> Dict[str, any]:
        """
        Validate uploaded file
        
        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            
        Returns:
            Dictionary with validation result
        """
        # Check file extension
        file_path = Path(filename)
        file_ext = file_path.suffix.lower()
        
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"Unsupported file type: {file_ext}. Allowed: {settings.ALLOWED_EXTENSIONS}"
            }
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {max_mb}MB"
            }
        
        return {"valid": True, "file_type": file_ext}
    
    def save_uploaded_file(self, file_data: bytes, filename: str, document_id: str) -> Path:
        """
        Save uploaded file to storage
        
        Args:
            file_data: Binary file data
            filename: Original filename
            document_id: Unique document identifier
            
        Returns:
            Path to saved file
        """
        # Create safe filename
        file_ext = Path(filename).suffix
        safe_filename = f"{document_id}{file_ext}"
        file_path = self.upload_dir / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"File saved to: {file_path}")
        return file_path
    
    def extract_text(self, file_path: Path, file_type: str) -> Optional[str]:
        """
        Extract text from document based on file type
        
        Args:
            file_path: Path to the document
            file_type: File extension (.pdf, .png, .jpg, .jpeg)
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info(f"Extracting text from {file_type} file: {file_path}")
            
            if file_type == '.pdf':
                raw_text = pdf_service.extract_text_from_pdf(file_path)
            elif file_type in ['.png', '.jpg', '.jpeg']:
                raw_text = ocr_service.extract_text_from_image(file_path)
            else:
                logger.error(f"Unsupported file type: {file_type}")
                return None
            
            if not raw_text:
                logger.warning(f"No text extracted from file: {file_path}")
                return None
            
            logger.info(f"Extracted {len(raw_text)} characters of raw text")
            return raw_text
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return None
    
    def clean_extracted_text(self, text: str) -> Optional[str]:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text or None if text is not meaningful
        """
        if not text:
            return None
        
        # Remove page numbers
        text = remove_page_numbers(text)
        
        # Clean text
        text = clean_text(text)
        
        # Check if text is meaningful
        cleaned = extract_meaningful_text(text)
        
        if cleaned:
            logger.info(f"Cleaned text: {len(cleaned)} characters")
        else:
            logger.warning("Text not meaningful after cleaning")
        
        return cleaned
    
    def process_document(self, file_data: bytes, filename: str, document_id: str) -> Dict[str, any]:
        """
        Complete document ingestion pipeline
        
        Args:
            file_data: Binary file data
            filename: Original filename
            document_id: Unique document identifier
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Validate file
            validation = self.validate_file(filename, len(file_data))
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"]
                }
            
            file_type = validation["file_type"]
            
            # Save file
            file_path = self.save_uploaded_file(file_data, filename, document_id)
            
            # Extract text
            raw_text = self.extract_text(file_path, file_type)
            if not raw_text:
                return {
                    "success": False,
                    "error": "Failed to extract text from document"
                }
            
            # Clean text
            cleaned_text = self.clean_extracted_text(raw_text)
            if not cleaned_text:
                return {
                    "success": False,
                    "error": "Document does not contain meaningful text"
                }
            
            return {
                "success": True,
                "file_path": str(file_path),
                "file_type": file_type,
                "extracted_text": cleaned_text,
                "text_length": len(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }


# Global ingestion agent instance
ingestion_agent = IngestionAgent()