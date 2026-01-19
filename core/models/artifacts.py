"""
Typed artifact models representing the document processing pipeline.
Each stage produces a typed artifact with clear contracts.

Pipeline: RawDoc → Page → Block → Chunk → EmbeddingRecord → ExtractionResult
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    UNKNOWN = "unknown"


class ExtractionMethod(str, Enum):
    TEXT = "text"  # Native PDF text extraction
    OCR = "ocr"  # Tesseract OCR
    HYBRID = "hybrid"  # Text + OCR fallback


@dataclass
class RawDoc:
    """Raw document artifact - initial upload."""
    doc_id: str
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    doc_type: DocumentType


@dataclass
class Page:
    """Page-level artifact - extracted from RawDoc."""
    page_number: int
    text: str
    extraction_method: ExtractionMethod
    has_images: bool = False
    has_tables: bool = False
    image_path: Optional[str] = None  # Path to page image if extracted
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Block:
    """Layout-aware block artifact - semantic units within a page."""
    block_id: str
    page_number: int
    block_type: str  # "text", "table", "header", "footer", "figure"
    text: str
    bbox: Optional[Dict[str, float]] = None  # Bounding box coordinates
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    """Chunk artifact - ready for embedding."""
    chunk_id: str
    page_number: int
    text: str
    block_id: Optional[str] = None
    char_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.char_count == 0:
            self.char_count = len(self.text)


@dataclass
class EmbeddingRecord:
    """Embedding artifact - vector representation."""
    chunk_id: str
    doc_id: str
    embedding: List[float]  # Vector representation
    model_name: str
    dim: int
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Final extraction artifact - structured data."""
    doc_id: str
    extraction_type: str  # "entities", "tables", "summary", "risks", etc.
    data: Dict[str, Any]  # Structured extraction data
    confidence: float
    evidence: List[Dict[str, Any]]  # Citations: [{chunk_id, page, score}]
    schema_version: str
    extracted_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentArtifacts:
    """Complete document artifact collection."""
    raw_doc: RawDoc
    pages: List[Page]
    blocks: List[Block] = field(default_factory=list)
    chunks: List[Chunk] = field(default_factory=list)
    embeddings: List[EmbeddingRecord] = field(default_factory=list)
    extractions: List[ExtractionResult] = field(default_factory=list)
    
    def get_chunks_by_page(self, page_number: int) -> List[Chunk]:
        """Get all chunks for a specific page."""
        return [c for c in self.chunks if c.page_number == page_number]
    
    def get_extractions_by_type(self, extraction_type: str) -> List[ExtractionResult]:
        """Get extractions by type."""
        return [e for e in self.extractions if e.extraction_type == extraction_type]
