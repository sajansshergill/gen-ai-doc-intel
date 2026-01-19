"""
Document ingestion pipeline.
Processes RawDoc → Page → Block → Chunk artifacts.
"""
from typing import List, Dict, Any
from pathlib import Path

from core.models.artifacts import (
    RawDoc, Page, Block, Chunk, DocumentType, ExtractionMethod
)
from core.extract.ocr import extract_text_from_pdf_images, extract_text_with_ocr
from core.extract.tables import extract_tables_from_pdf
from core.ingest.chunk import chunk_pages as chunk_pages_func
from pypdf import PdfReader


class DocumentProcessor:
    """Processes documents through the ingestion pipeline."""
    
    def __init__(self, use_ocr_fallback: bool = True):
        self.use_ocr_fallback = use_ocr_fallback
    
    def process(self, raw_doc: RawDoc) -> Dict[str, Any]:
        """
        Process RawDoc through the pipeline.
        
        Returns:
            Dict with pages, blocks, and chunks
        """
        if raw_doc.doc_type == DocumentType.PDF:
            return self._process_pdf(raw_doc)
        elif raw_doc.doc_type == DocumentType.IMAGE:
            return self._process_image(raw_doc)
        else:
            raise ValueError(f"Unsupported document type: {raw_doc.doc_type}")
    
    def _process_pdf(self, raw_doc: RawDoc) -> Dict[str, Any]:
        """Process PDF document."""
        pages = []
        blocks = []
        
        # Try text extraction first
        reader = PdfReader(raw_doc.file_path)
        total_chars = 0
        
        for i, pdf_page in enumerate(reader.pages):
            text = pdf_page.extract_text() or ""
            total_chars += len(text)
            
            # Determine extraction method
            if len(text.strip()) < 50 and self.use_ocr_fallback:
                # Very little text, likely scanned - use OCR
                try:
                    ocr_pages = extract_text_from_pdf_images(raw_doc.file_path)
                    if i < len(ocr_pages):
                        text = ocr_pages[i].get("text", text)
                        method = ExtractionMethod.OCR
                    else:
                        method = ExtractionMethod.TEXT
                except Exception:
                    method = ExtractionMethod.TEXT
            else:
                method = ExtractionMethod.TEXT
            
            # Create Page artifact
            page = Page(
                page_number=i + 1,
                text=text,
                extraction_method=method,
                has_images=False,  # Could detect images
                has_tables=False   # Will detect tables separately
            )
            pages.append(page)
        
        # Extract tables
        try:
            tables_data = extract_tables_from_pdf(raw_doc.file_path)
            # Mark pages with tables
            for table in tables_data:
                page_num = table.get("page", 1)
                if page_num <= len(pages):
                    pages[page_num - 1].has_tables = True
                    
                    # Create Block artifact for table
                    block = Block(
                        block_id=f"table_{page_num}_{table.get('table_index', 0)}",
                        page_number=page_num,
                        block_type="table",
                        text=table.get("text", ""),
                        metadata={"table_data": table.get("data", [])}
                    )
                    blocks.append(block)
        except Exception:
            pass  # Table extraction failed, continue
        
        # Create text blocks
        for page in pages:
            if page.text.strip():
                block = Block(
                    block_id=f"text_{page.page_number}",
                    page_number=page.page_number,
                    block_type="text",
                    text=page.text
                )
                blocks.append(block)
        
        # Chunk pages
        page_dicts = [
            {"page": p.page_number, "text": p.text}
            for p in pages
        ]
        chunk_objects = chunk_pages_func(page_dicts, chunk_size=800, overlap=120)
        
        # Convert to Chunk artifacts
        chunks = [
            Chunk(
                chunk_id=c.chunk_id,
                page_number=c.page,
                text=c.text,
                char_count=len(c.text)
            )
            for c in chunk_objects
        ]
        
        return {
            "pages": pages,
            "blocks": blocks,
            "chunks": chunks,
            "total_chars": total_chars
        }
    
    def _process_image(self, raw_doc: RawDoc) -> Dict[str, Any]:
        """Process image document."""
        # Extract text using OCR
        text = extract_text_with_ocr(raw_doc.file_path)
        
        # Create single page
        page = Page(
            page_number=1,
            text=text,
            extraction_method=ExtractionMethod.OCR,
            has_images=True
        )
        
        # Create block
        block = Block(
            block_id="image_1",
            page_number=1,
            block_type="text",
            text=text
        )
        
        # Chunk
        page_dicts = [{"page": 1, "text": text}]
        chunk_objects = chunk_pages_func(page_dicts, chunk_size=800, overlap=120)
        
        chunks = [
            Chunk(
                chunk_id=c.chunk_id,
                page_number=c.page,
                text=c.text,
                char_count=len(c.text)
            )
            for c in chunk_objects
        ]
        
        return {
            "pages": [page],
            "blocks": [block],
            "chunks": chunks,
            "total_chars": len(text)
        }
