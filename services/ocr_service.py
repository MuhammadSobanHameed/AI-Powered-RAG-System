"""
OCR Service
Handles Optical Character Recognition for image documents
"""
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """
    Service for extracting text from images using Tesseract OCR
    """
    
    def __init__(self):
        """Initialize OCR service"""
        # Tesseract should be installed on the system
        # For Linux: sudo apt-get install tesseract-ocr
        # For Mac: brew install tesseract
        # For Windows: download from https://github.com/UB-Mannheim/tesseract/wiki
        pass
    
    def extract_text_from_image(self, image_path: Path) -> Optional[str]:
        """
        Extract text from an image file using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info(f"Starting OCR extraction for: {image_path}")
            
            # Open image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            if not text or len(text.strip()) == 0:
                logger.warning(f"No text extracted from image: {image_path}")
                return None
            
            logger.info(f"Successfully extracted {len(text)} characters from image")
            return text
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {str(e)}")
            return None
    
    def extract_text_from_image_with_preprocessing(self, image_path: Path) -> Optional[str]:
        """
        Extract text with image preprocessing for better accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Optional: Apply thresholding or other preprocessing
            # This can be expanded based on image quality
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            return text if text and len(text.strip()) > 0 else None
            
        except Exception as e:
            logger.error(f"OCR with preprocessing failed for {image_path}: {str(e)}")
            return None


# Global OCR service instance
ocr_service = OCRService()