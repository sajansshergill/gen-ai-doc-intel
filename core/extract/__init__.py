"""Document extraction modules: OCR, tables, etc."""
from .ocr import extract_text_with_ocr, extract_text_from_pdf_images
from .tables import extract_tables_from_pdf

__all__ = [
    "extract_text_with_ocr",
    "extract_text_from_pdf_images",
    "extract_tables_from_pdf"
]
