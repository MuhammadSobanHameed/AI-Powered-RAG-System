"""
PDF Service
Handles text extraction from PDF documents
"""
import PyPDF2
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for extracting text from PDF documents
    """
    
    def __init__(self):
        """Initialize PDF service"""
        pass
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info(f"Starting PDF text extraction for: {pdf_path}")
            
            # Open PDF file
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                # Extract text from all pages
                text_parts = []
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text:
                            text_parts.append(page_text)
                            logger.debug(f"Extracted text from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                # Combine all text
                full_text = '\n\n'.join(text_parts)
                
                if not full_text or len(full_text.strip()) == 0:
                    logger.warning(f"No text extracted from PDF: {pdf_path}")
                    return None
                
                logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
                return full_text
                
        except Exception as e:
            logger.error(f"PDF extraction failed for {pdf_path}: {str(e)}")
            return None
    
    def get_pdf_metadata(self, pdf_path: Path) -> dict:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'num_pages': len(pdf_reader.pages),
                    'author': metadata.get('/Author', 'Unknown'),
                    'title': metadata.get('/Title', 'Unknown'),
                    'subject': metadata.get('/Subject', 'Unknown'),
                    'creator': metadata.get('/Creator', 'Unknown'),
                }
        except Exception as e:
            logger.error(f"Failed to extract PDF metadata: {str(e)}")
            return {}


# Global PDF service instance
pdf_service = PDFService()