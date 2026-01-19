"""
GenAI Document Intelligence Platform API
Production-grade system with typed artifacts, batch/realtime separation,
and evaluation guardrails.
"""
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from pathlib import Path

# Core components
from core.models.artifacts import (
    RawDoc, Page, Block, Chunk, EmbeddingRecord, ExtractionResult,
    DocumentType, ExtractionMethod, DocumentArtifacts
)
from core.storage.interface import LocalStorage, StorageBackend

# Type hints for lazy-loaded modules
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.embeddings.local_embedder import LocalEmbedder
    from core.vectorstore.faiss_store import FaissStore
    from core.llm.reasoning import LLMReasoner
    from core.multimodal.layout_caption import LayoutCaptioner
    from core.eval.validation import EvaluationHarness
    from pipelines.ingestion.document_processor import DocumentProcessor
    from pipelines.embeddings.batch_processor import BatchEmbeddingProcessor
# Lazy imports to avoid segfaults on module load
from core.ingest.chunk import chunk_pages
from core.extract.ocr import extract_text_from_pdf_images, extract_text_with_ocr
from core.extract.tables import extract_tables_from_pdf
from core.schemas.outputs import QueryResponse, DocumentExtraction, Citation
from core.schemas.extractions import RiskSummaryV1, Entity, KPIMetric

# These will be imported lazily to avoid segfault
# from core.embeddings.local_embedder import LocalEmbedder
# from core.vectorstore.faiss_store import FaissStore
# from core.llm.reasoning import LLMReasoner
# from core.multimodal.layout_caption import LayoutCaptioner
# from core.eval.validation import EvaluationHarness
# from pipelines.ingestion.document_processor import DocumentProcessor
# from pipelines.embeddings.batch_processor import BatchEmbeddingProcessor

app = FastAPI(
    title="GenAI Document Intelligence Platform",
    description="Production-grade GenAI system for document understanding, extraction, and querying",
    version="1.0.0"
)

# CORS middleware for GitHub Pages and local development
# Allow all origins in development, restrict in production via environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    # For GitHub Pages, we need to allow all origins or use a function
    # In production, set ALLOWED_ORIGINS to specific domains
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for GitHub Pages compatibility
        allow_credentials=False,  # Can't use credentials with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request Models
class QueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    doc_ids: Optional[List[str]] = None
    use_llm: bool = True
    response_schema: Optional[str] = Field(None, description="Schema name: RiskSummaryV1, DocumentSummary, etc.")


class ExtractRequest(BaseModel):
    doc_id: str
    extract_tables: bool = True
    extract_entities: bool = True
    generate_summary: bool = True


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
INDEX_DIR = PROJECT_ROOT / "data" / "index"
WEB_DIR = PROJECT_ROOT / "apps" / "web" / "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# Serve static files (web UI)
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.get("/")
async def root():
    """Serve the web UI."""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "GenAI Document Intelligence Platform API", "docs": "/docs"}

# Initialize components (lazy where needed to avoid segfaults)
storage: StorageBackend = LocalStorage(str(UPLOAD_DIR))
embedder = None
store = None
llm_reasoner = None
document_processor = None
batch_processor = None
layout_captioner = None
evaluator = None

# Document registry (in production, use proper DB)
document_registry: Dict[str, DocumentArtifacts] = {}


def get_embedder():
    """Lazy initialization of embedder."""
    global embedder
    if embedder is None:
        from core.embeddings.local_embedder import LocalEmbedder
        embedder = LocalEmbedder()
    return embedder


def get_store():
    """Lazy initialization of vector store."""
    global store
    if store is None:
        from core.vectorstore.faiss_store import FaissStore
        store = FaissStore(index_dir=str(INDEX_DIR), dim=384)
    return store


def get_llm_reasoner():
    """Lazy initialization of LLM reasoner."""
    global llm_reasoner
    if llm_reasoner is None:
        from core.llm.reasoning import LLMReasoner
        provider = os.getenv("LLM_PROVIDER", "openai")
        try:
            llm_reasoner = LLMReasoner(provider=provider)
        except Exception as e:
            print(f"Warning: LLM initialization failed: {e}. Running in retrieval-only mode.")
            llm_reasoner = None
    return llm_reasoner


def get_document_processor():
    """Lazy initialization of document processor."""
    global document_processor
    if document_processor is None:
        from pipelines.ingestion.document_processor import DocumentProcessor
        document_processor = DocumentProcessor()
    return document_processor


def get_batch_processor():
    """Lazy initialization of batch processor."""
    global batch_processor
    if batch_processor is None:
        from pipelines.embeddings.batch_processor import BatchEmbeddingProcessor
        batch_processor = BatchEmbeddingProcessor()
    return batch_processor


def get_evaluator():
    """Lazy initialization of evaluator."""
    global evaluator
    if evaluator is None:
        from core.eval.validation import EvaluationHarness
        evaluator = EvaluationHarness()
    return evaluator


def get_layout_captioner():
    """Lazy initialization of layout captioner."""
    global layout_captioner
    if layout_captioner is None:
        from core.multimodal.layout_caption import LayoutCaptioner
        layout_captioner = LayoutCaptioner()
    return layout_captioner


def determine_doc_type(filename: str) -> DocumentType:
    """Determine document type from filename."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return DocumentType.PDF
    elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
        return DocumentType.IMAGE
    return DocumentType.UNKNOWN


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "components": {
            "embedder": embedder is not None,
            "vector_store": store is not None,
            "llm": llm_reasoner is not None
        }
    }


@app.post("/v1/documents")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Upload and process a document.
    Returns doc_id and status immediately, processes in background.
    """
    doc_id = str(uuid.uuid4())
    
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    doc_type = determine_doc_type(file.filename)
    
    if doc_type == DocumentType.UNKNOWN:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
    
    # Check file size (limit to 10MB for free tier)
    file_size = 0
    try:
        # Save file
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")
    
    # Create RawDoc artifact
    raw_doc = RawDoc(
        doc_id=doc_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        content_type=file.content_type or "application/pdf",
        uploaded_at=datetime.now(),
        doc_type=doc_type
    )
    
    # Process document in background to avoid timeout
    def process_document():
        try:
            processed = get_document_processor().process(raw_doc)
            pages = processed["pages"]
            blocks = processed["blocks"]
            chunks = processed["chunks"]
            
            # Generate embeddings (batch)
            embeddings = get_batch_processor().process_chunks(chunks, doc_id)
            
            # Add to vector store
            vectors = [e.embedding for e in embeddings]
            metadatas = [
                {
                    "doc_id": doc_id,
                    "filename": file.filename,
                    "chunk_id": c.chunk_id,
                    "page": c.page_number,
                    "text": c.text,
                }
                for c in chunks
            ]
            get_store().add(vectors, metadatas)
            
            # Create DocumentArtifacts
            doc_artifacts = DocumentArtifacts(
                raw_doc=raw_doc,
                pages=pages,
                blocks=blocks,
                chunks=chunks,
                embeddings=embeddings
            )
            document_registry[doc_id] = doc_artifacts
            
            # Extract tables if PDF
            if doc_type == DocumentType.PDF:
                try:
                    tables_data = extract_tables_from_pdf(str(file_path))
                    # Store tables count in registry if needed
                except Exception as e:
                    print(f"Table extraction error: {e}")
        except Exception as e:
            print(f"Background processing error for {doc_id}: {e}")
            # Store error state
            document_registry[doc_id] = DocumentArtifacts(
                raw_doc=raw_doc,
                pages=[],
                blocks=[],
                chunks=[],
                embeddings=[]
            )
    
    # Always process in background to prevent timeout
    import threading
    thread = threading.Thread(target=process_document)
    thread.daemon = True
    thread.start()
    
    # Also add to FastAPI background tasks if available
    if background_tasks:
        background_tasks.add_task(process_document)
    
    # Return immediately
    return {
        "doc_id": doc_id,
        "status": "uploaded",
        "filename": file.filename,
        "pages": 0,  # Will be updated after processing
        "chunks": 0,  # Will be updated after processing
        "tables": 0,
        "extraction_method": "processing",
        "message": "Document uploaded successfully. Processing in background..."
    }


@app.get("/v1/documents/{doc_id}")
async def get_document(doc_id: str) -> Dict[str, Any]:
    """Get document metadata and available artifacts."""
    if doc_id not in document_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    artifacts = document_registry[doc_id]
    
    return {
        "doc_id": doc_id,
        "filename": artifacts.raw_doc.filename,
        "uploaded_at": artifacts.raw_doc.uploaded_at.isoformat(),
        "pages": len(artifacts.pages),
        "chunks": len(artifacts.chunks),
        "blocks": len(artifacts.blocks),
        "embeddings": len(artifacts.embeddings),
        "extractions": len(artifacts.extractions),
        "extraction_method": artifacts.pages[0].extraction_method.value if artifacts.pages else "unknown"
    }


@app.get("/v1/documents/{doc_id}/chunks")
async def get_chunks(doc_id: str, page: Optional[int] = None) -> Dict[str, Any]:
    """Get chunks for a document, optionally filtered by page."""
    if doc_id not in document_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    artifacts = document_registry[doc_id]
    chunks = artifacts.chunks
    
    if page:
        chunks = [c for c in chunks if c.page_number == page]
    
    return {
        "doc_id": doc_id,
        "chunks": [
            {
                "chunk_id": c.chunk_id,
                "page": c.page_number,
                "text": c.text[:200] + "..." if len(c.text) > 200 else c.text,
                "char_count": c.char_count
            }
            for c in chunks
        ],
        "total": len(chunks)
    }


@app.get("/v1/documents/{doc_id}/tables")
async def get_tables(doc_id: str) -> Dict[str, Any]:
    """Get extracted tables for a document."""
    if doc_id not in document_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    artifacts = document_registry[doc_id]
    tables = [b for b in artifacts.blocks if b.block_type == "table"]
    
    return {
        "doc_id": doc_id,
        "tables": [
            {
                "block_id": t.block_id,
                "page": t.page_number,
                "text": t.text[:500] + "..." if len(t.text) > 500 else t.text,
                "metadata": t.metadata
            }
            for t in tables
        ],
        "total": len(tables)
    }


@app.post("/v1/query", response_model=QueryResponse)
async def query_documents(payload: QueryRequest) -> QueryResponse:
    """
    Query documents with semantic search + LLM reasoning.
    Returns schema-validated response with evidence.
    """
    question = payload.question.strip()
    top_k = payload.top_k
    doc_ids = payload.doc_ids
    use_llm = payload.use_llm
    
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    
    # Retrieve relevant chunks
    qvec = get_embedder().embed_query(question)
    results = get_store().search(qvec, top_k=top_k)
    
    # Filter by doc_ids if provided
    if doc_ids and len(doc_ids) > 0:
        results = [r for r in results if r.get("doc_id") in set(doc_ids)]
    
    if not results:
        return QueryResponse(
            question=question,
            answer="No relevant documents found.",
            citations=[],
            evidence=[],
            confidence=0.0
        )
    
    # Build evidence list
    evidence = [
        {
            "doc_id": r["doc_id"],
            "filename": r.get("filename"),
            "page": r["page"],
            "chunk_id": r["chunk_id"],
            "score": r["score"],
            "snippet": (r["text"][:240] + ("..." if len(r["text"]) > 240 else "")),
        }
        for r in results
    ]
    
    # Build citations
    citations = [
        Citation(
            doc_id=r["doc_id"],
            filename=r.get("filename"),
            page=r["page"],
            chunk_id=r.get("chunk_id"),
            score=r.get("score")
        )
        for r in results
    ]
    
    # Generate answer using LLM if enabled
    if use_llm:
        reasoner = get_llm_reasoner()
        if reasoner:
            # Map schema name to schema class if needed
            schema_map = {
                "RiskSummaryV1": RiskSummaryV1,
                # Add more schemas as needed
            }
            response_schema = schema_map.get(payload.response_schema) if payload.response_schema else None
            
            llm_response = reasoner.generate_answer(question, results, response_schema)
            answer = llm_response.get("answer", "")
            if isinstance(answer, dict):
                answer = answer.get("answer", str(answer))
        else:
            # Fallback: simple concatenation
            answer = "\n\n".join([f"[Page {r['page']}] {r['text']}" for r in results[:3]])
    else:
        # Simple retrieval-only mode
        answer = "\n\n".join([f"[Page {r['page']}] {r['text']}" for r in results[:3]])
    
    # Calculate confidence (average of top scores)
    confidence = sum(r.get("score", 0) for r in results[:3]) / min(len(results), 3) if results else 0.0
    
    # Evaluate response quality
    eval_result = get_evaluator().evaluate_response(
        {"answer": answer, "citations": [c.dict() for c in citations]},
        results
    )
    
    response = QueryResponse(
        question=question,
        answer=answer[:2000],  # Limit answer length
        citations=citations,
        evidence=evidence,
        confidence=confidence
    )
    
    # Add evaluation metadata (can be in response or separate endpoint)
    # For now, we'll log it or return in a separate field
    
    return response


@app.post("/v1/documents/{doc_id}/extract")
async def extract_document_features(
    doc_id: str,
    request: ExtractRequest
) -> Dict[str, Any]:
    """
    Extract additional features: tables, entities, summary.
    Uses LLM for structured extraction.
    """
    if doc_id not in document_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    artifacts = document_registry[doc_id]
    result = {
        "doc_id": doc_id,
        "filename": artifacts.raw_doc.filename,
        "tables": [],
        "entities": [],
        "summary": None
    }
    
    # Extract tables
    if request.extract_tables:
        tables = [b for b in artifacts.blocks if b.block_type == "table"]
        result["tables"] = [
            {
                "block_id": t.block_id,
                "page": t.page_number,
                "text": t.text[:500],
                "metadata": t.metadata
            }
            for t in tables
        ]
    
    # Extract entities and generate summary (requires LLM)
    if request.extract_entities or request.generate_summary:
        reasoner = get_llm_reasoner()
        if reasoner:
            # Get all document text
            all_text = "\n\n".join([c.text for c in artifacts.chunks])
            
            # Generate summary
            if request.generate_summary:
                summary_prompt = f"Summarize this document in 3-5 key points:\n\n{all_text[:3000]}"
                summary_response = reasoner.generate_answer(summary_prompt, [])
                result["summary"] = summary_response.get("answer", "")
            
            # Extract entities (simplified - in production use NER models)
            if request.extract_entities:
                entity_prompt = f"Extract key entities (people, organizations, dates, amounts) from:\n\n{all_text[:3000]}"
                entity_response = reasoner.generate_answer(entity_prompt, [])
                result["entities"] = []  # TODO: Parse structured entities
        else:
            result["note"] = "LLM not configured. Set OPENAI_API_KEY or GEMINI_API_KEY for entity extraction and summarization."
    
    return result


@app.get("/v1/documents")
async def list_documents() -> Dict[str, Any]:
    """List all uploaded documents."""
    return {
        "documents": [
            {
                "doc_id": doc_id,
                "filename": artifacts.raw_doc.filename,
                "uploaded_at": artifacts.raw_doc.uploaded_at.isoformat(),
                "pages": len(artifacts.pages),
                "chunks": len(artifacts.chunks)
            }
            for doc_id, artifacts in document_registry.items()
        ],
        "total": len(document_registry)
    }


@app.post("/v1/evaluate")
async def evaluate_response(
    response: Dict[str, Any],
    evidence_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate a query response for faithfulness, hallucinations, and schema compliance.
    Useful for testing and quality assurance.
    """
    eval_result = get_evaluator().evaluate_response(response, evidence_chunks)
    return eval_result
