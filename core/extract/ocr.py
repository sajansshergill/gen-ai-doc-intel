"""
OCR module for extracting text from scanned PDFs and images.
Uses Tesseract OCR as the primary engine.
"""
import io
from typing import List, Dict, Any, Optional

try:
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    convert_from_path = None


def extract_text_with_ocr(image_path: str, lang: str = "eng") -> str:
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_path: Path to the image file
        lang: Language code (default: "eng")
    
    Returns:
        Extracted text string
    """
    if not OCR_AVAILABLE:
        return "[OCR not available: Install pytesseract and pdf2image]"
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        return f"[OCR Error: {str(e)}]"


def extract_text_from_pdf_images(pdf_path: str, dpi: int = 300) -> List[Dict[str, Any]]:
    """
    Convert PDF pages to images and extract text using OCR.
    Useful for scanned PDFs that don't have extractable text.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for image conversion (higher = better quality but slower)
    
    Returns:
        List of dicts with page number and extracted text
    """
    if not OCR_AVAILABLE:
        return [{
            "page": 1,
            "text": "[OCR not available: Install pytesseract and pdf2image]",
            "method": "ocr_unavailable"
        }]
    
    pages = []
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        for i, image in enumerate(images):
            # Convert PIL image to text using OCR
            text = pytesseract.image_to_string(image, lang="eng")
            pages.append({
                "page": i + 1,
                "text": text.strip(),
                "method": "ocr"
            })
    except Exception as e:
        # Fallback: return error info
        pages.append({
            "page": 1,
            "text": f"[OCR Error: {str(e)}]",
            "method": "ocr_error"
        })
    
    return pages
