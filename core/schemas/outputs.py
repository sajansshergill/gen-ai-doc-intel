"""
Pydantic schemas for structured API outputs.
These ensure schema-validated JSON responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation for a source."""
    doc_id: str
    filename: Optional[str] = None
    page: int
    chunk_id: Optional[str] = None
    score: Optional[float] = None


class Entity(BaseModel):
    """Extracted entity."""
    name: str
    type: str  # e.g., "person", "organization", "date", "amount"
    value: str
    page: Optional[int] = None
    confidence: Optional[float] = None


class Table(BaseModel):
    """Extracted table."""
    page: int
    table_index: int
    rows: int
    columns: int
    data: List[List[str]]
    text: str  # Text representation for embedding


class Summary(BaseModel):
    """Document summary."""
    doc_id: str
    filename: str
    summary: str
    key_points: List[str]
    page_count: int
    entities: List[Entity] = []


class QueryResponse(BaseModel):
    """Structured response to a query."""
    question: str
    answer: str
    citations: List[Citation]
    evidence: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Retrieved chunks used to generate answer"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score for the answer"
    )


class DocumentExtraction(BaseModel):
    """Complete extraction from a document."""
    doc_id: str
    filename: str
    pages: int
    text_chunks: int
    tables: List[Table] = []
    entities: List[Entity] = []
    summary: Optional[Summary] = None
    extraction_method: str = "text"  # "text", "ocr", or "hybrid"
